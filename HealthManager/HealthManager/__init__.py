try:
    from .routes import qwen_bp
except ImportError:
    from routes import qwen_bp

__all__ = ['qwen_bp']
