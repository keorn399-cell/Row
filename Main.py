import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from newfile import main as game_main
        game_main()
    except Exception as e:
        print(f"Ошибка запуска игры: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
