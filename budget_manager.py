"""Interactive budget manager.

Allows entering plan metadata, budget categories and spending updates,
then produces execution reports. Supports a non-interactive demo mode
to show sample usage/output.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Category:
    name: str
    budget: float
    spent: float = 0.0
    notes: List[str] = field(default_factory=list)

    @property
    def remaining(self) -> float:
        return self.budget - self.spent

    @property
    def execution_rate(self) -> float:
        if self.budget == 0:
            return 0.0
        return (self.spent / self.budget) * 100


class BudgetManager:
    def __init__(self, plan_name: str, start_date: str, end_date: str):
        self.plan_name = plan_name
        self.start_date = start_date
        self.end_date = end_date
        self.categories: Dict[str, Category] = {}

    def add_category(self, name: str, budget: float) -> None:
        if name in self.categories:
            raise ValueError(f"科目『{name}』已存在，請改用其他名稱。")
        self.categories[name] = Category(name=name, budget=budget)

    def add_categories_from_csv(self, csv_path: Path) -> None:
        if not csv_path.exists():
            raise FileNotFoundError(f"找不到檔案: {csv_path}")

        with csv_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            expected = {"科目", "經費額度"}
            if not expected.issubset(reader.fieldnames or {}):
                raise ValueError("CSV 欄位需包含：科目、經費額度")
            for row in reader:
                name = row["科目"].strip()
                if not name:
                    continue
                budget = float(row["經費額度"].replace(",", "").strip())
                if name in self.categories:
                    self.categories[name].budget += budget
                else:
                    self.categories[name] = Category(name=name, budget=budget)

    def record_spending(self, name: str, amount: float, note: Optional[str] = None) -> None:
        if name not in self.categories:
            raise KeyError(f"找不到科目『{name}』，請先建立科目。")
        self.categories[name].spent += amount
        if note:
            self.categories[name].notes.append(note)

    def summary(self) -> str:
        lines = [
            f"計畫：{self.plan_name}",
            f"期程：{self.start_date} ~ {self.end_date}",
            "",
            "科目\t額度\t已執行\t執行率\t剩餘",
        ]
        for category in self.categories.values():
            lines.append(
                f"{category.name}\t"
                f"{category.budget:,.0f}\t"
                f"{category.spent:,.0f}\t"
                f"{category.execution_rate:.1f}%\t"
                f"{category.remaining:,.0f}"
            )

        total_budget = sum(c.budget for c in self.categories.values())
        total_spent = sum(c.spent for c in self.categories.values())
        total_remaining = total_budget - total_spent
        total_rate = (total_spent / total_budget * 100) if total_budget else 0.0
        lines.extend(
            [
                "",
                "總計",
                f"額度：{total_budget:,.0f}",
                f"已執行：{total_spent:,.0f}",
                f"執行率：{total_rate:.1f}%",
                f"剩餘：{total_remaining:,.0f}",
            ]
        )
        return "\n".join(lines)


def prompt_float(message: str) -> float:
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("請輸入有效數字。")


def interactive_session() -> None:
    print("=== 經費管理 ===")
    plan_name = input("計畫名稱：")
    start_date = input("開始日期（YYYY-MM-DD，可留空）：")
    end_date = input("結束日期（YYYY-MM-DD，可留空）：")

    manager = BudgetManager(plan_name, start_date, end_date)

    while True:
        print("\n1) 新增科目\n2) CSV 匯入科目\n3) 登記支出\n4) 查看報表\n5) 離開")
        choice = input("選擇操作：").strip()

        try:
            if choice == "1":
                name = input("科目名稱：").strip()
                budget = prompt_float("經費額度：")
                manager.add_category(name, budget)
                print(f"已新增科目 {name}")
            elif choice == "2":
                path = Path(input("CSV 路徑：").strip())
                manager.add_categories_from_csv(path)
                print("匯入完成。")
            elif choice == "3":
                name = input("科目名稱：").strip()
                amount = prompt_float("支出金額：")
                note = input("說明（可留空）：").strip() or None
                manager.record_spending(name, amount, note)
                print("已記錄支出。")
            elif choice == "4":
                print("\n" + manager.summary())
            elif choice == "5":
                print("離開，謝謝使用。")
                break
            else:
                print("請輸入 1-5 之間的選項。")
        except Exception as exc:  # noqa: BLE001 - 提示使用者錯誤即可
            print(f"操作失敗：{exc}")


def demo_run() -> None:
    print("=== 示範模式：經費管理 ===")
    manager = BudgetManager("AI 研究計畫", "2024-01-01", "2024-12-31")
    manager.add_category("人事費", 1_200_000)
    manager.add_category("設備費", 500_000)
    manager.add_category("旅運費", 150_000)

    manager.record_spending("人事費", 300_000, "1-3 月薪資")
    manager.record_spending("設備費", 120_000, "伺服器升級")
    manager.record_spending("旅運費", 45_000, "出差車票與住宿")

    print("已建立示範資料，以下為報表：\n")
    print(manager.summary())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="簡易經費管理工具")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="以示範資料直接輸出執行畫面（不需互動）",
    )
    args = parser.parse_args()

    if args.demo:
        demo_run()
    else:
        interactive_session()
