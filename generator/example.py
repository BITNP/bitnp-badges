import json
from pathlib import Path
from badge_generator import BadgeGenerator
from uuid import uuid4
generator = BadgeGenerator()
badge_data = generator.generate_badge({"标题": "测试纪念章", "姓名": "张三", "学号": "123456", "角色": "成员", "纪念章ID": str(uuid4())})

current_dir = Path(__file__).parent
Path(current_dir / "badges").mkdir(parents=True, exist_ok=True)
with open(current_dir / "badges" / "example_badge.json", "w") as f:
    json.dump(badge_data, f, ensure_ascii=False)
