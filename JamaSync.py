import os

import requests

# 設定
BASE_URL = "https://acceleratedsoftware.jamacloud.com/rest/latest"
username = os.environ['JAMA_USERNAME'] 
password = os.environ['JAMA_PASSWORD']

AUTH = (username, password)

def get_syncable_fields(item_type_id):
    """
    アイテムタイプの定義を取得し、synchronizeがtrueのフィールド名のリストを返す
    """
    url = f"{BASE_URL}/itemtypes/{item_type_id}"
    response = requests.get(url, auth=AUTH)
    response.raise_for_status()
    
    fields = response.json()['data']['fields']
    # synchronizeがtrueのフィールドのみを抽出
    return [f['name'] for f in fields if f.get('synchronize') is True]

def prepare_patch_payload(source_data, syncable_fields):
    """
    ソースデータのうち、同期可能なフィールドだけをPATCH用に整形する
    """
    payload = []
    for key, value in source_data.items():
        if key in syncable_fields:
            payload.append({
                "op": "replace",
                "path": f"/fields/{key}",
                "value": value
            })
        else:
            print(f"Skipping field '{key}': Not marked for synchronization.")
    return payload

def sync_jama_item(item_id, item_type_id, source_data):
    """
    メインの同期処理
    """
    # 1. 同期可能なフィールド名を定義から取得
    syncable_fields = get_syncable_fields(item_type_id)
    
    # 2. 更新用ペイロードを作成
    patch_payload = prepare_patch_payload(source_data, syncable_fields)
    
    # 3. 更新実行
    if patch_payload:
        url = f"{BASE_URL}/items/{item_id}"
        response = requests.patch(url, auth=AUTH, json=patch_payload)
        response.raise_for_status()
        print(f"Item {item_id} successfully updated.")
    else:
        print("No valid fields to synchronize.")

# --- 使用例 ---
if __name__ == "__main__":
    TARGET_ITEM_ID = 196734
    TARGET_TYPE_ID = 160  # ASE Risk
    
    # 更新したいデータの例
    update_data = {
        "name": "Updated Risk Name",         # syncable: true
        "description": "New description",    # syncable: true
        "globalId": "ShouldBeIgnored"        # syncable: false (無視される)
    }
    
    sync_jama_item(TARGET_ITEM_ID, TARGET_TYPE_ID, update_data)