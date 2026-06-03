import os
import json
import logging
import base64
from flask import Blueprint, request, jsonify, current_app
from dashscope import MultiModalConversation
from openai import OpenAI
from utils import success_response, error_response, validate_required_fields

ai_services_bp = Blueprint('ai_services', __name__)
logger = logging.getLogger(__name__)

def get_tuantuan_api_key():
    """获取团团烹饪助手的API Key"""
    return os.getenv('DASHSCOPE_API_KEY_TUANTUAN')

@ai_services_bp.route('/api/ai/image-generation', methods=['POST'])
def generate_image():
    """
    文生图API - 使用qwen-image-2.0模型
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(400, '请求数据格式错误')
        
        prompt = data.get('prompt', '').strip()
        
        is_valid, error_msg = validate_required_fields(data, ['prompt'])
        if not is_valid:
            return error_response(400, error_msg)
        
        if len(prompt) > 500:
            return error_response(400, '提示词不能超过500字')
        
        api_key = get_tuantuan_api_key()
        if not api_key:
            return error_response(500, 'API Key未配置')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ]
        
        try:
            response = MultiModalConversation.call(
                api_key=api_key,
                model="qwen-image-2.0",
                messages=messages,
                result_format='message',
                stream=False,
                n=1,
                watermark=False,
                negative_prompt="""
            )
            
            logger.info(f"Image generation response: {response}")
            
            if response.status_code == 200:
                try:
                    result = response.output.choices[0].message.content
                    logger.info(f"Content type: {type(result)}, Content: {result}")
                    
                    if isinstance(result, list) and len(result) > 0:
                        first_item = result[0]
                        if isinstance(first_item, dict):
                            image_url = first_item.get('url') or first_item.get('image')
                        else:
                            image_url = str(first_item)
                    elif isinstance(result, dict):
                        image_url = result.get('url') or result.get('image')
                    else:
                        image_url = str(result) if result else None
                    
                    if image_url:
                        return success_response({
                            'image_url': image_url,
                            'prompt': prompt
                        }, '图片生成成功')
                    else:
                        logger.error(f"无法提取图片URL, result: {result}")
                        return error_response(500, f'图片生成失败:未返回图片URL, result={result}')
                except Exception as e:
                    logger.error(f"解析图片生成结果失败: {str(e)}", exc_info=True)
                    return error_response(500, f'图片生成结果解析失败:{str(e)}')
            else:
                logger.error(f"Image generation failed: {response.message}")
                return error_response(500, f'图片生成失败:{response.message})
                
        except Exception as e:
            logger.error(f"Error calling image generation API: {str(e)}", exc_info=True)
            return error_response(500, f'图片生成API调用失败:{str(e)}')
            
    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}", exc_info=True)
        return error_response(500, f'内部服务器错误:{str(e)}')

@ai_services_bp.route('/api/ai/image-analysis', methods=['POST'])
def analyze_image():
    """
    视觉理解API - 使用qwen3.5-flash模型进行美食图片打分
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(400, '请求数据格式错误')
        
        image_url = data.get('image_url', '').strip()
        image_base64 = data.get('image_base64', '').strip()
        
        if not image_url and not image_base64:
            return error_response(400, '请提供图片URL或base64编码')
        
        api_key = get_tuantuan_api_key()
        if not api_key:
            return error_response(500, 'API Key未配置')
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        system_prompt = """你是一位专业的美食评价专家。请对用户上传的美食图片进行评价,包括:
1. 食材识别:识别图片中的主要食材
2. 菜品分析:分析菜品的烹饪技巧、摆盘、色彩搭配等
3. 评分:给出1-10分的评分(10分为最高分)
4. 建议:给出改进建议或赞美

请以JSON格式返回结果,格式如下:
{
    "ingredients": ["食材1", "食材2"],
    "analysis": "菜品分析描述",
    "score": 8.5,
    "suggestion": "改进建议或赞美",
    "exp_reward": 15
}

评分标准:
- 9-10分:色香味俱全,摆盘精美,烹饪技巧高超
- 7-8分:味道不错,摆盘良好,有一定创意
- 5-6分:基本合格,但还有提升空间
- 1-4分:需要改进

经验值奖励规则:
- 9-10分:奖励25经验值
- 7-8分:奖励20经验值
- 5-6分:奖励15经验值
- 1-4分:奖励10经验值"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if image_url:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": "请评价这道美食"}
                ]
            })
        elif image_base64:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    {"type": "text", "text": "请评价这道美食"}
                ]
            })
        
        try:
            completion = client.chat.completions.create(
                model="qwen3.5-flash",
                messages=messages,
                extra_body={"enable_thinking": True},
                stream=False
            )
            
            if completion and completion.choices and len(completion.choices) > 0:
                response_text = completion.choices[0].message.content
                
                try:
                    result = json.loads(response_text)
                    
                    return success_response({
                        'ingredients': result.get('ingredients', []),
                        'analysis': result.get('analysis', ''),
                        'score': result.get('score', 5.0),
                        'suggestion': result.get('suggestion', ''),
                        'exp_reward': result.get('exp_reward', 10)
                    }, '图片分析成功')
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {response_text}")
                    return error_response(500, '解析分析结果失败')
            else:
                return error_response(500, '图片分析失败:未返回结果')
                
        except Exception as e:
            logger.error(f"Error calling image analysis API: {str(e)}", exc_info=True)
            return error_response(500, f'图片分析API调用失败:{str(e)}')
            
    except Exception as e:
        logger.error(f"Error in analyze_image: {str(e)}", exc_info=True)
        return error_response(500, f'内部服务器错误:{str(e)}')

@ai_services_bp.route('/api/ai/chat-with-image', methods=['POST'])
def chat_with_image():
    """
    带图片的对话API - 使用qwen3.5-flash模型
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(400, '请求数据格式错误')
        
        message = data.get('message', '').strip()
        image_url = data.get('image_url', '').strip()
        conversation_id = data.get('conversation_id', '').strip()
        
        if not message and not image_url:
            return error_response(400, '请提供消息或图片')
        
        api_key = get_tuantuan_api_key()
        if not api_key:
            return error_response(500, 'API Key未配置')
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        system_prompt = """你是团团,一位专业的烹饪助手。你的任务是:
1. 回答用户关于烹饪的问题
2. 提供专业的烹饪建议
3. 当用户上传美食图片时,识别食材并给出评价
4. 语气要亲切友好,像一位经验丰富的厨师

请用简洁明了的中文回答,避免使用过多的Markdown格式标记。""""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        user_content = []
        if image_url:
            user_content.append({"type": "image_url", "image_url": {"url": image_url}})
        if message:
            user_content.append({"type": "text", "text": message})
        
        messages.append({"role": "user", "content": user_content})
        
        try:
            completion = client.chat.completions.create(
                model="qwen3.5-flash",
                messages=messages,
                extra_body={"enable_thinking": True},
                stream=False
            )
            
            if completion and completion.choices and len(completion.choices) > 0:
                response_text = completion.choices[0].message.content
                
                return success_response({
                    'response': response_text,
                    'conversation_id': conversation_id
                }, '对话成功')
            else:
                return error_response(500, '对话失败:未返回结果')
                
        except Exception as e:
            logger.error(f"Error calling chat API: {str(e)}", exc_info=True)
            return error_response(500, f'对话API调用失败:{str(e)}')
            
    except Exception as e:
        logger.error(f"Error in chat_with_image: {str(e)}", exc_info=True)
        return error_response(500, f'内部服务器错误:{str(e)}')
