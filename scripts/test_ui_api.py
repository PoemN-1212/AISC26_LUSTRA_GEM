import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("Testing live upgraded FastAPI endpoint http://localhost:8000/api/consultation/chat...")
    
    payload = json.dumps({"message": "tôi muốn làm một đồ án OLAP về bank transaction fraud ấy"}).encode('utf-8')
    req = urllib.request.Request(
        "http://localhost:8000/api/consultation/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode('utf-8'))
    
    print("\n✅ HTTP STATUS: 200 OK")
    print("Domain:", d.get("blueprint", {}).get("domain"))
    print("Target Role:", d.get("blueprint", {}).get("target_role"))
    print("\nTailored Layer 1 Components:")
    for c in d.get("blueprint", {}).get("layer1_core", {}).get("components", []):
        print(f"  * {c.get('category')}: {c.get('tech')} -> {c.get('purpose')}")
        
    print("\nLayer 2 Boosters (Real TopCV):")
    for b in d.get("blueprint", {}).get("layer2_boosters", []):
        print(f"  * {b.get('skill')}: {b.get('market_evidence')}")
        
    print("\nLayer 3 Extension:")
    l3 = d.get("blueprint", {}).get("layer3_extension", {})
    print(f"  * {l3.get('proposed_module')}: {l3.get('technologies')} -> {l3.get('cv_value')}")
    
    print("\nReply Excerpt:")
    print(d.get("reply", "")[:350] + "...")

if __name__ == "__main__":
    main()
