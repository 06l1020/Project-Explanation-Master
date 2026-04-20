"""
Token使用记录器

负责记录和管理所有LLM调用的token消耗信息
"""

from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json


class TokenUsageRecord:
    """单次token使用记录"""
    
    def __init__(
        self,
        operation: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        timestamp: Optional[str] = None
    ):
        """
        初始化token使用记录
        
        Args:
            operation: 操作类型（如"项目分析"、"知识点讲解"、"问答"）
            model: 使用的模型名称
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            total_tokens: 总token数
            timestamp: 时间戳（ISO格式）
        """
        self.operation = operation
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'operation': self.operation,
            'model': self.model,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'TokenUsageRecord':
        """从字典创建记录"""
        return TokenUsageRecord(
            operation=data['operation'],
            model=data['model'],
            prompt_tokens=data['prompt_tokens'],
            completion_tokens=data['completion_tokens'],
            total_tokens=data['total_tokens'],
            timestamp=data.get('timestamp')
        )


class TokenUsageTracker:
    """
    Token使用追踪器
    
    功能：
    1. 记录每次LLM调用的token消耗
    2. 计算累计token使用量
    3. 导出token使用报告
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        初始化token追踪器
        
        Args:
            project_path: 项目路径（用于保存token记录文件）
        """
        self.records: List[TokenUsageRecord] = []
        self.project_path = Path(project_path) if project_path else None
        self.token_file = self.project_path / "token_usage.json" if self.project_path else None
        
        # 如果文件存在，加载历史记录
        if self.token_file and self.token_file.exists():
            self._load_records()
    
    def add_record(
        self,
        operation: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ):
        """
        添加token使用记录
        
        Args:
            operation: 操作类型
            model: 模型名称
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            total_tokens: 总token数
        """
        record = TokenUsageRecord(
            operation=operation,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
        self.records.append(record)
        
        # 自动保存到文件
        self._save_records()
    
    def get_total_usage(self) -> Dict[str, int]:
        """
        获取累计token使用量
        
        Returns:
            包含总token数的字典
        """
        total_prompt = sum(r.prompt_tokens for r in self.records)
        total_completion = sum(r.completion_tokens for r in self.records)
        total_all = sum(r.total_tokens for r in self.records)
        
        return {
            'total_prompt_tokens': total_prompt,
            'total_completion_tokens': total_completion,
            'total_tokens': total_all,
            'call_count': len(self.records)
        }
    
    def get_usage_by_operation(self) -> Dict[str, Dict[str, int]]:
        """
        按操作类型统计token使用
        
        Returns:
            按操作类型分组的token使用统计
        """
        stats = {}
        
        for record in self.records:
            op = record.operation
            if op not in stats:
                stats[op] = {
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0,
                    'call_count': 0
                }
            
            stats[op]['prompt_tokens'] += record.prompt_tokens
            stats[op]['completion_tokens'] += record.completion_tokens
            stats[op]['total_tokens'] += record.total_tokens
            stats[op]['call_count'] += 1
        
        return stats
    
    def get_records(self) -> List[Dict]:
        """获取所有记录（字典列表）"""
        return [r.to_dict() for r in self.records]
    
    def clear_records(self):
        """清除所有记录"""
        self.records = []
        if self.token_file:
            self._save_records()
    
    def _save_records(self):
        """保存记录到文件"""
        if not self.token_file:
            return
        
        try:
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [r.to_dict() for r in self.records]
            
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 保存token记录失败: {e}")
    
    def _load_records(self):
        """从文件加载记录"""
        if not self.token_file or not self.token_file.exists():
            return
        
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.records = [TokenUsageRecord.from_dict(r) for r in data]
            
        except Exception as e:
            print(f"⚠️ 加载token记录失败: {e}")
            self.records = []
    
    def generate_report(self) -> str:
        """
        生成token使用报告
        
        Returns:
            格式化的报告文本
        """
        total = self.get_total_usage()
        by_op = self.get_usage_by_operation()
        
        report = "# Token消耗报告\n\n"
        report += f"**统计时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "---\n\n"
        
        report += "## 总体统计\n\n"
        report += f"- **总调用次数：** {total['call_count']} 次\n"
        report += f"- **总输入Token：** {total['total_prompt_tokens']:,}\n"
        report += f"- **总输出Token：** {total['total_completion_tokens']:,}\n"
        report += f"- **总Token消耗：** {total['total_tokens']:,}\n\n"
        
        report += "---\n\n"
        report += "## 按操作类型统计\n\n"
        report += "| 操作类型 | 调用次数 | 输入Token | 输出Token | 总Token |\n"
        report += "|---------|---------|----------|----------|--------|\n"
        
        for op, stats in by_op.items():
            report += f"| {op} | {stats['call_count']} | {stats['prompt_tokens']:,} | {stats['completion_tokens']:,} | {stats['total_tokens']:,} |\n"
        
        report += "\n---\n\n"
        report += "## 详细记录\n\n"
        report += "| 时间 | 操作 | 模型 | 输入Token | 输出Token | 总Token |\n"
        report += "|------|------|------|----------|----------|--------|\n"
        
        for record in reversed(self.records):  # 最新记录在前
            time_str = datetime.fromisoformat(record.timestamp).strftime('%Y-%m-%d %H:%M')
            report += f"| {time_str} | {record.operation} | {record.model} | {record.prompt_tokens:,} | {record.completion_tokens:,} | {record.total_tokens:,} |\n"
        
        return report
