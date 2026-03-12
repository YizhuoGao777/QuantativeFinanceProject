import csv

input_file = 'data.csv'
output_file = 'cleaned_data.csv'

def is_valid_row(row):
    # 只要有任何字段是 "N/A"，就认为该行无效
    return all(value != "N/A" for value in row.values())

def clean_csv(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames  # 保留原字段名
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()  # 写入表头

        for row in reader:
            if is_valid_row(row):
                writer.writerow(row)

if __name__ == '__main__':
    clean_csv(input_file, output_file)
    print(f"清洗完成，已保存为 {output_file}")