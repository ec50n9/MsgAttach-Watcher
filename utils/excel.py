from typing import Dict, List
import openpyxl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

def save_dict_to_excel(data: List[Dict[str, str]], filename: str):
  workbook = openpyxl.Workbook()
  worksheet = workbook.active

  headers = list(data[0].keys())
  worksheet.append(headers)

  for row in data:
    row = [fix_illegal_characters(row[header]) for header in headers]
    worksheet.append(row)

  workbook.save(filename)

def fix_illegal_characters(text: str) -> str:
  return ILLEGAL_CHARACTERS_RE.sub('', text)