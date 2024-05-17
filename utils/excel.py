from typing import Dict, List
import openpyxl

def save_dict_to_excel(data: List[Dict[str, str]], filename: str):
  workbook = openpyxl.Workbook()
  worksheet = workbook.active

  headers = list(data[0].keys())
  worksheet.append(headers)

  for row in data:
    row = [str(row[header]) for header in headers]
    worksheet.append(row)

  workbook.save(filename)