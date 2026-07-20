import csv
from pathlib import Path


def gen_compare_performance_report(
    summaries: dict[str, Path | str], 
    output_path: Path | str, 
    columns: list[str]
) -> None:
    output_path = Path(output_path)
    
    all_data = {}
    all_keys = set()
    
    for prefix, path in summaries.items():
        summary_path = Path(path)
        all_data[prefix] = {}
        
        if summary_path.exists():
            with open(summary_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (row["group"], row["test_name"])
                    all_data[prefix][key] = row
                    all_keys.add(key)
                    
    sorted_keys = sorted(list(all_keys))
    
    header = ["group", "test_name"]
    for col in columns:
        for prefix in summaries.keys():
            header.append(f"{prefix}_{col}")
            
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for key in sorted_keys:
            group, test_name = key
            row_data = [group, test_name]
            
            for col in columns:
                for prefix in summaries.keys():
                    prefix_data = all_data[prefix].get(key, {})
                    row_data.append(prefix_data.get(col, "-"))
                    
            writer.writerow(row_data)