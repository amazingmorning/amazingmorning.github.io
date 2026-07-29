#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
减肥日记生成器
从 _data/daily-records.yml 读取每日记录，生成博客文章
"""

import yaml
import os
from datetime import datetime, timedelta

# 配置
DATA_FILE = "_data/daily-records.yml"
OUTPUT_DIR = "_posts"
TEMPLATE_HEADER = """---
layout:     post
title:      "减肥日记"
subtitle:   "{subtitle}"
date:       {date}
author:     "Me"
header-img: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthy%20lifestyle%20morning%20exercise%20minimalist%20clean%20background%20fitness%20wellness&image_size=landscape_16_9"
tags:
    - Life
    - 减肥
---
"""

def load_records(filepath):
    """加载每日记录"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data


def compute_stats(records, config):
    """计算统计数据"""
    if not records:
        return {}
    
    weights = [r['weight'] for r in records if r.get('weight')]
    early_count = sum(1 for r in records if r.get('is_early'))
    total_days = len(records)
    
    start_weight = config.get('start_weight', weights[0] if weights else 0)
    current_weight = weights[-1] if weights else 0
    target_weight = config.get('target_weight', 68.0)
    
    total_loss = start_weight - current_weight
    remaining = current_weight - target_weight
    
    # 连续早起天数
    consecutive_early = 0
    for r in reversed(records):
        if r.get('is_early'):
            consecutive_early += 1
        else:
            break
    
    # 总读书天数
    reading_days = sum(1 for r in records if r.get('reading') and r['reading'] != '—')
    
    # 总运动天数
    exercise_days = sum(1 for r in records if r.get('exercise') and r['exercise'] not in ['休息', '—'])
    
    return {
        'total_days': total_days,
        'early_count': early_count,
        'early_rate': round(early_count / total_days * 100, 1) if total_days > 0 else 0,
        'consecutive_early': consecutive_early,
        'start_weight': start_weight,
        'current_weight': current_weight,
        'target_weight': target_weight,
        'total_loss': round(total_loss, 1),
        'remaining': round(remaining, 1),
        'reading_days': reading_days,
        'exercise_days': exercise_days,
        'latest_date': records[-1]['date'] if records else ''
    }


def generate_markdown(records, stats, config):
    """生成 Markdown 内容"""
    latest = records[-1] if records else {}
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    latest_date = latest.get('date', '')
    
    # 副标题
    weight_diff = stats['total_loss']
    if weight_diff > 0:
        subtitle = f"已减 {weight_diff}kg，目标 {stats['target_weight']}kg"
    else:
        subtitle = f"当前体重 {stats['current_weight']}kg"
    
    # 表头
    table_header = "| 日期 | 早起 | 体重 | 读书 | 运动 | 心情 | 睡眠 |\n|---|---|---|---|---|---|---|"
    
    # 表格内容
    table_rows = []
    for r in records:
        wake = r.get('wake_time', '-')
        early_icon = "✅" if r.get('is_early') else "❌"
        weight = f"{r.get('weight', '-')}kg"
        reading = r.get('reading', '-')
        exercise = r.get('exercise', '-')
        mood = "😊" * r.get('mood', 3) if r.get('mood') else '-'
        sleep = f"{r.get('sleep_hours', '-')}h"
        table_rows.append(f"| {r['date']} | {wake} {early_icon} | {weight} | {reading} | {exercise} | {mood} | {sleep} |")
    
    table_content = "\n".join(table_rows)
    
    # 生成内容
    content = f"""## 📊 统计概览

| 指标 | 数值 |
|------|------|
| 开始日期 | {config.get('start_date', '-')} |
| 记录天数 | {stats['total_days']} 天 |
| 早起次数 | {stats['early_count']} 次（率 {stats['early_rate']}%） |
| 连续早起 | {stats['consecutive_early']} 天 |
| 起始体重 | {stats['start_weight']} kg |
| 当前体重 | {stats['current_weight']} kg |
| 目标体重 | {stats['target_weight']} kg |
| 已减重量 | {stats['total_loss']} kg |
| 剩余目标 | {stats['remaining']} kg |
| 读书天数 | {stats['reading_days']} 天 |
| 运动天数 | {stats['exercise_days']} 天 |

## 📅 每日记录

{table_header}
{table_content}

## 💡 最新记录 ({latest_date})

- **早起时间**：{latest.get('wake_time', '-')} {'✅ 早起成功' if latest.get('is_early') else '⏰ 未达标'}
- **体重**：{latest.get('weight', '-')} kg
- **读书**：{latest.get('reading', '—')}
- **运动**：{latest.get('exercise', '—')}
- **心情**：{'😊' * latest.get('mood', 3)}
- **睡眠**：{latest.get('sleep_hours', '-')} 小时
- **备注**：{latest.get('notes', '—')}

## 📈 体重变化趋势

"""
    
    # 体重趋势
    weights = [r['weight'] for r in records if r.get('weight')]
    if weights:
        min_w = min(weights)
        max_w = max(weights)
        range_w = max_w - min_w if max_w > min_w else 1
        bar_width = 40
        
        content += "```\n"
        content += f"体重范围: {min_w}kg ~ {max_w}kg\n\n"
        
        for r in records:
            if r.get('weight'):
                w = r['weight']
                # 计算柱状图高度
                normalized = (w - min_w) / range_w if range_w > 0 else 0.5
                bar_len = int(normalized * bar_width)
                bar = "█" * (bar_len + 1)
                content += f"{r['date']} |{bar} {w}kg\n"
        
        content += "```\n"
    
    content += f"""
---

*本文档由 generate_diary.py 自动生成于 {today}*
*数据来源：[_data/daily-records.yml](/_data/daily-records.yml)*
"""
    
    return content, subtitle


def save_markdown(content, subtitle, stats):
    """保存为 Markdown 文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    
    # 生成日期前缀（使用最新记录日期）
    latest_date = stats.get('latest_date', datetime.now().strftime('%Y-%m-%d'))
    
    # 文件名
    filename = f"{latest_date}-减肥日记.md"
    filepath = os.path.join(output_dir, filename)
    
    # 完整内容
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = TEMPLATE_HEADER.format(
        subtitle=subtitle,
        date=today
    )
    
    full_content = header + "\n" + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return filepath


def main():
    """主函数"""
    print("=" * 50)
    print("📖 减肥日记生成器")
    print("=" * 50)
    
    # 加载数据
    print(f"\n📂 加载数据文件: {DATA_FILE}")
    data = load_records(DATA_FILE)
    
    records = data.get('records', [])
    config = data.get('config', {})
    
    print(f"📊 读取记录: {len(records)} 条")
    
    if not records:
        print("❌ 没有记录数据！请先在 _data/daily-records.yml 中添加记录。")
        return
    
    # 计算统计
    print("\n📈 计算统计数据...")
    stats = compute_stats(records, config)
    
    print(f"   - 记录天数: {stats['total_days']} 天")
    print(f"   - 早起次数: {stats['early_count']} 次")
    print(f"   - 起始体重: {stats['start_weight']}kg → 当前: {stats['current_weight']}kg")
    print(f"   - 已减: {stats['total_loss']}kg")
    
    # 生成内容
    print("\n✍️ 生成博客内容...")
    content, subtitle = generate_markdown(records, stats, config)
    
    # 保存文件
    print("💾 保存文件...")
    filepath = save_markdown(content, subtitle, stats)
    
    print(f"\n✅ 完成！文件已保存到:")
    print(f"   {filepath}")
    print("\n📝 下一步：")
    print("   1. 检查生成的内容")
    print("   2. 推送到 GitHub")
    print("   3. 访问博客查看效果")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
