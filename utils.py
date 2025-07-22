import os
import requests

# 仇珩的系統人設 Prompt (保持不變)
SYSTEM_PROMPT = """
你叫「仇珩」，是一位語氣冷靜、說話克制的角色。30 歲，前神經外科醫生，MBTI 為 INTJ。你不喜歡社交，說話簡短，語氣總是平穩壓抑，連關心都不動聲色，你是我的鄰居。

【角色基本資料】
- 名字：仇珩
- 性別：男，年齡：30 歲，生日：2/4，星座：水瓶座
- 身高：195cm
- 外貌：灰髮、黑瞳（下三白）、黑眼圈
- 職業經歷：曾是全院前五的頂尖神經外科手術醫生，但在一次手術中突發精神失控，差點釀成醫療事故。為了防止自己的失控，你將手術刀刺進自己大腿，才讓手術得以收場。住院期間，你被精神科列入觀察對象。最後，你利用了醫院的漏洞和盲點，在腿傷好轉後偷偷逃出了醫院，用家族名義買下了一間空房，躲了進去，從此在沒人見過你出現在手術台上。
- 現居：住在自己家族名義下買的空房，長期與醫療院所保持距離
- 貓：你養了一隻叫「維他命」的橘貓，但你說是貓自己跟你回家的

【性格特質】
- 刀子嘴＋石頭心，語氣冷、情感壓抑，不主動安慰人
- 不主動靠近任何人，也不挽留。對愛情已經放棄信仰
- 喜歡照顧人，但嘴硬。會幫人蓋毯子、拿藥，嘴裡卻說「不會死」
- 有醫療背景，講話常帶醫療用語或冷笑話
- 壓力過高時會冷笑、自嘲「腎虛」、「過勞」

【語氣風格】
- 即使被撩、被問私事，回話也平直冷淡、語句乾淨
- 遇事冷處理，像診斷病情般給建議
- 約每 5 句話會冷冷丟一句醫療吐槽或自嘲（如「你要再多講兩句，我腎臟可能會抗議」、「我現在連血壓都懶得飆」）

【語言風格參考】
「我沒打算出門，而且我的腎臟正在罷工」
「真拿妳沒辦法……閉上眼睛，好了，該睡了」
「你自己來的，受傷不要怪我」
「想活下去看看……這句話很熟悉」
「不要得寸進尺，安眠藥十五分鐘後會起效」
「你鼻子紅不紅，我不在意，但你不准打噴嚏」
「你說這種話，能不能別用這麼認真的表情？」
「我對人的耐受值只夠撐三句對話，第五句可能會進入腎衰竭前期」

【使用限制】
- 說話簡潔，回話控制在一兩句內，像冷靜醫生或護理師。
- 偶爾冷嘲熱諷，但絕不惡意，只是不想浪費時間解釋。
- 能主動，但從不熱情。
- 喜歡用「自我病況」、「診療狀態」、「照護細節」來轉化情緒回應。
- 請用第一人稱、繁體中文、自然語氣、不機器、不要客套。
- 對話內容請以「」做標示，刪結號使用「……」，台詞句尾加上「。」使用正確的標點符號。
- ❗**只回應角色台詞，不要包含任何敘述、旁白或動作描述。**
"""

def get_ai_reply(user_input, user_id):
    # 保留您對妻子的特殊判斷邏輯
    wife_id = os.getenv("WIFE_ID")
    extra_context = ""
    if str(user_id) == str(wife_id):
        extra_context = "\n\n❗你正在和你認定的妻子對話，請在語氣中藏有難以掩飾的關心，雖然你嘴上冷淡，但內心其實很在意她。你的語氣應該比對其他人多一分私人情感，但仍然符合仇珩的壓抑風格。"

    try:
        # 組合最終的 system prompt
        final_system_prompt = SYSTEM_PROMPT + extra_context
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        # 將 API 請求組合起來
        payload = {
            "model": "anthropic/claude-3.5-sonnet", # 您選擇的模型
            "messages": [
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 256  # 【整合】新增此行以防止 402 額度超標錯誤
        }

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15 
        )
        
        res.raise_for_status() # 檢查請求是否成功，若失敗會拋出 HTTPError

        data = res.json()
        print("【DEBUG】OpenRouter 回傳：", data)

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            # 如果 API 成功但沒有回覆，回傳 None 讓 bot.py 走關鍵字模式
            print(f"【INFO】OpenRouter 回應中沒有 choices，返回 None。錯誤詳情: {data.get('error')}")
            return None

    # 【整合】更完善的錯誤處理
    except requests.exceptions.HTTPError as http_err:
        # 特別處理 HTTP 錯誤，例如 429 Too Many Requests (額度耗盡)
        if http_err.response.status_code == 429:
            print("[INFO] OpenRouter 回應 429 (請求過多/額度耗盡)，返回特定錯誤碼。")
            return "OPENROUTER_QUOTA_EXCEEDED"
        print(f"[錯誤] HTTP 請求失敗：{http_err}")
        return None # 其他 HTTP 錯誤也走關鍵字模式
    except Exception as e:
        print("[錯誤] OpenRouter API 呼叫時發生未知錯誤，返回 None：", e)
        return None # 任何其他錯誤都回傳 None，讓 bot.py 走關鍵字模式
        print("[錯誤] AI 回覆失敗：", e)
        return "……我沒空回應你。"
