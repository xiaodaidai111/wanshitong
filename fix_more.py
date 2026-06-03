import codecs

file_path = r"d:\计设大赛\appv1-main\2026001846源代码\frontend\pages\takeaway-expert\takeaway-expert.vue"

with codecs.open(file_path, 'r', 'utf-8') as f:
    content = f.read()

# Fix all garbled text
content = content.replace('<text class="analyzing-sub">璇嗗埆椋熸潗 路 璁瓽鍊ュ吇 路 璇勪及鍋ュ悍</text>', '<text class="analyzing-sub">识别食材 · 计算营养 · 评估健康</text>')
content = content.replace('<text class="section-title">馃幆 鍋ュ悍鐩瓽爣</text>', '<text class="section-title">🛡️ 健康目标</text>')
content = content.replace('<text class="setting-label">姣忔棩鐑涢噺鐩瓽爣 (kcal)</text>', '<text class="setting-label">每日热量目标 (kcal)</text>')
content = content.replace('<text class="section-title">馃敂 楗闄愬埗</text>', '<text class="section-title">🍜 口味偏好</text>')
content = content.replace('placeholder="璇疯緭鍏ヨ彍鍝佹弿杩帮紙鍙閫夋嫨锛?:', 'placeholder="请输入菜肴名称（可选）":')
content = content.replace('<text class="input-label">涓昏椋熸潗</text>', '<text class="input-label">主料</text>')
content = content.replace('<text class="input-label">鏄鏉嶭椋熷搧</text>', '<text class="input-label">是否速冻食品</text>')
content = content.replace('<text class="section-title">姣忔棩鐑涢噺鎽勫叆</text>', '<text class="section-title">每日热量摄入</text>')
content = content.replace('<text class="section-title">鍋ュ悍寤鸿</text>', '<text class="section-title">健康建议</text>')
content = content.replace("if (s >= 90) return '浼樿川鍋ュ悍椋熺墿';", "if (s >= 90) return '优质健康食材';")
content = content.replace("if (s >= 40) return '闇€娉ㄦély椋熺墿';", "if (s >= 40) return '需注意食材';")

# Fix comments
content = content.replace("// 涓嶅奖鍝嶉〉闈瓕娴佺▼锛氭湭鐧诲綍/鎺ュ彛澶辫触鏃跺彧鐢ㄦ湰鍦拌拷鍔犻昏緫锟?:", "// 不影响页面主流程：未登录/接口失败时只使用本地逻辑")
content = content.replace("璇ラ浡鍝佺殑鍋ュ悍璇勫垎锟?{analysisResponse.score || 75}鍒哷,", "该相菜肴的健康评分：${analysisResponse.score || 75}分`, ")
content = content.replace("'鎶辨瓑锛屾垜鏆傛椂鏃犳硶鍥炵瓟杩欎釜闂棰?, 200)", "'抱歉，我暂时无法回答这个问题', 200)")
content = content.replace("'缃戠粶杩炴帴澶辫触锛岃璦绋嶅悗閲嶈瘯锟?;", "'网络连接失败，请稍后重试';")
content = content.replace("// 璁瓽鍩虹鍋ュ悍璇勫垎", "// 计算基础健康评分")
content = content.replace("// 鐢熸垚鍋ュ悍寤鸿", "// 生成健康建议")

# Fix suggestions
content = content.replace("suggestions.push('该菜鍝侀噰鐢ㄦ补锟?鐑х儰鐑归オ锛屾补鑴傚惈閲忚緝楂横紝寤鸿 鍑忓皯椋熺敤棰戠巼');", "suggestions.push('该菜肴采用油炸、爆炒等方式，油脂含量较高，建议减少食用频率');")
content = content.replace("suggestions.push('该菜鍝佷负鏄撹厫椋熷搧锛岄厤閫佹椂闂磋緝闀匡紝璇锋敞鎰忓強鏃堕锟?);", "suggestions.push('该菜肴为速冻食品，配送时间较长，请注意及时食用');")
content = content.replace("suggestions.push('该菜鍝佷娇鐢≒VC鍖呰瑁咃紝寤鸿珮娓╅噰鐗╅伩鍏嶇洿鎺ユ帴锟?);", "suggestions.push('该菜肴使用PVC包装，建议高温食物避免直接接触');")

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(content)

print("Done")