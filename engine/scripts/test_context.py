from scripts.utils.context_loader import loader
import json

def test():
    print("Testing Context Loader for br/winner777/stg...")
    config = loader.load("br", "winner777", "stg")
    
    print(json.dumps(config, indent=2, ensure_ascii=False))

    # Assertions to verify merging
    assert config['currency'] == 'BRL'  # Overridden by Region
    assert config['brand_name'] == 'Winner 777' # From App
    assert config['db']['host'] == 'stg-db.winner777.com' # From Env
    assert config['timeout'] == 30 # From Global
    
    print("\n✅ Context Loader Verified Successfully!")

if __name__ == "__main__":
    test()
