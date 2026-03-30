"""
监测报告生成器
支持生成PDF格式的鸟类监测报告
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, ListFlowable, ListItem
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timedelta
import os
import io


class ReportGenerator:
    """鸟类监测报告生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """设置中文字体和样式"""
        # 尝试注册中文字体
        try:
            # Windows系统常用中文字体
            font_paths = [
                'C:/Windows/Fonts/simhei.ttf',  # 黑体
                'C:/Windows/Fonts/simsun.ttc',  # 宋体
                'C:/Windows/Fonts/msyh.ttc',    # 微软雅黑
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_name = os.path.basename(font_path).split('.')[0]
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    self.chinese_font = 'ChineseFont'
                    break
            else:
                self.chinese_font = 'Helvetica'
        except:
            self.chinese_font = 'Helvetica'
        
        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.chinese_font,
            fontSize=24,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # 副标题样式
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # 章节标题样式
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY
        )
        
        # 表格标题样式
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        )
        
        # 表格内容样式
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            alignment=TA_LEFT
        )
    
    def generate_report(self, report_data, output_path=None):
        """
        生成监测报告
        
        Args:
            report_data: 报告数据字典
            output_path: 输出路径，为None则返回字节流
        
        Returns:
            如果output_path为None，返回PDF字节流；否则返回文件路径
        """
        if output_path:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
        else:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
        
        # 构建报告内容
        story = []
        
        # 封面
        self._add_cover(story, report_data)
        
        # 分页
        story.append(PageBreak())
        
        # 概述
        self._add_summary(story, report_data)
        
        # 观测统计
        self._add_observation_stats(story, report_data)
        
        # 物种分布
        self._add_species_distribution(story, report_data)
        
        # 濒危物种
        if report_data.get('endangered_species'):
            self._add_endangered_species(story, report_data)
        
        # 设备统计
        self._add_device_stats(story, report_data)
        
        # 生成PDF
        doc.build(story)
        
        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer.getvalue()
    
    def _add_cover(self, story, data):
        """添加封面"""
        # 空行占位
        for _ in range(6):
            story.append(Spacer(1, 1*cm))
        
        # 标题
        title = Paragraph("鸟类监测数据分析报告", self.title_style)
        story.append(title)
        
        # 副标题
        subtitle = Paragraph(
            f"{data.get('area_name', '西溪湿地')}自然保护区",
            self.subtitle_style
        )
        story.append(subtitle)
        
        story.append(Spacer(1, 2*cm))
        
        # 报告信息
        info_data = [
            [Paragraph("报告周期：", self.body_style), 
             Paragraph(data.get('date_range', '-'), self.body_style)],
            [Paragraph("生成时间：", self.body_style), 
             Paragraph(datetime.now().strftime('%Y年%m月%d日 %H:%M'), self.body_style)],
            [Paragraph("报告编号：", self.body_style), 
             Paragraph(f"BIRD-{datetime.now().strftime('%Y%m%d')}-{data.get('report_id', '001')}", self.body_style)],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
    
    def _add_summary(self, story, data):
        """添加概述"""
        heading = Paragraph("一、监测概述", self.heading_style)
        story.append(heading)
        
        summary_text = f"""
        本次监测周期为{data.get('date_range', '-')}, 
        共记录到<strong>{data.get('total_observations', 0)}</strong>条有效观测记录，
        涉及<strong>{data.get('total_species', 0)}</strong>个鸟类物种。
        其中发现<strong>{data.get('endangered_count', 0)}</strong>种濒危物种（EN/CR/VU级别），
        占观测物种总数的{data.get('endangered_percentage', 0)}%。
        监测覆盖{data.get('device_count', 0)}个观测设备，数据完整率达到{data.get('completeness_rate', 0)}%。
        """
        
        summary = Paragraph(summary_text, self.body_style)
        story.append(summary)
        story.append(Spacer(1, 0.5*cm))
    
    def _add_observation_stats(self, story, data):
        """添加观测统计"""
        heading = Paragraph("二、观测统计", self.heading_style)
        story.append(heading)
        
        # 统计数据表格
        stats_data = [
            [Paragraph('统计指标', self.table_header_style), 
             Paragraph('数值', self.table_header_style),
             Paragraph('说明', self.table_header_style)],
            [Paragraph('总观测记录', self.table_cell_style), 
             Paragraph(str(data.get('total_observations', 0)), self.table_cell_style),
             Paragraph('已确认的有效观测记录', self.table_cell_style)],
            [Paragraph('物种总数', self.table_cell_style), 
             Paragraph(str(data.get('total_species', 0)), self.table_cell_style),
             Paragraph('观测到的不同物种数量', self.table_cell_style)],
            [Paragraph('个体总数', self.table_cell_style), 
             Paragraph(str(data.get('total_individuals', 0)), self.table_cell_style),
             Paragraph('所有观测个体数量之和', self.table_cell_style)],
            [Paragraph('濒危物种数', self.table_cell_style), 
             Paragraph(str(data.get('endangered_count', 0)), self.table_cell_style),
             Paragraph('EN/CR/VU级别物种', self.table_cell_style)],
            [Paragraph('平均置信度', self.table_cell_style), 
             Paragraph(f"{data.get('avg_confidence', 0)}%", self.table_cell_style),
             Paragraph('AI识别平均置信度', self.table_cell_style)],
        ]
        
        stats_table = Table(stats_data, colWidths=[4*cm, 3*cm, 6*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.5*cm))
    
    def _add_species_distribution(self, story, data):
        """添加物种分布"""
        heading = Paragraph("三、物种分布", self.heading_style)
        story.append(heading)
        
        # Top10物种表格
        species_list = data.get('top_species', [])
        if species_list:
            table_data = [
                [Paragraph('排名', self.table_header_style),
                 Paragraph('物种名称', self.table_header_style),
                 Paragraph('学名', self.table_header_style),
                 Paragraph('观测次数', self.table_header_style),
                 Paragraph('保护级别', self.table_header_style)]
            ]
            
            for idx, species in enumerate(species_list[:10], 1):
                conservation = species.get('conservation_status', '-')
                conservation_color = self._get_conservation_color(conservation)
                
                row = [
                    Paragraph(str(idx), self.table_cell_style),
                    Paragraph(species.get('chinese_name', '-'), self.table_cell_style),
                    Paragraph(f"<i>{species.get('scientific_name', '-')}</i>", self.table_cell_style),
                    Paragraph(str(species.get('observation_count', 0)), self.table_cell_style),
                    Paragraph(conservation, self.table_cell_style),
                ]
                table_data.append(row)
            
            species_table = Table(table_data, colWidths=[1.5*cm, 4*cm, 4*cm, 2*cm, 2*cm])
            species_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (2, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            
            story.append(species_table)
        else:
            story.append(Paragraph("暂无物种分布数据", self.body_style))
        
        story.append(Spacer(1, 0.5*cm))
    
    def _add_endangered_species(self, story, data):
        """添加濒危物种详情"""
        heading = Paragraph("四、濒危物种详情", self.heading_style)
        story.append(heading)
        
        endangered_list = data.get('endangered_species', [])
        
        for species in endangered_list:
            # 物种标题
            species_title = Paragraph(
                f"• {species.get('chinese_name', '-')} ({species.get('scientific_name', '-')})",
                ParagraphStyle(
                    'SpeciesTitle',
                    parent=self.body_style,
                    fontSize=12,
                    textColor=colors.HexColor('#dc3545'),
                    spaceAfter=6
                )
            )
            story.append(species_title)
            
            # 物种信息
            info_text = f"""
            <b>保护级别：</b>{species.get('conservation_status', '-')} | 
            <b>观测次数：</b>{species.get('observation_count', 0)} | 
            <b>观测数量：</b>{species.get('total_count', 0)}只
            """
            story.append(Paragraph(info_text, self.body_style))
            
            if species.get('description'):
                story.append(Paragraph(
                    f"<b>物种简介：</b>{species['description'][:150]}...",
                    self.body_style
                ))
            
            story.append(Spacer(1, 0.3*cm))
        
        story.append(Spacer(1, 0.5*cm))
    
    def _add_device_stats(self, story, data):
        """添加设备统计"""
        heading = Paragraph("五、设备监测情况", self.heading_style)
        story.append(heading)
        
        device_list = data.get('device_stats', [])
        if device_list:
            table_data = [
                [Paragraph('设备编号', self.table_header_style),
                 Paragraph('位置', self.table_header_style),
                 Paragraph('观测记录', self.table_header_style),
                 Paragraph('物种数', self.table_header_style)]
            ]
            
            for device in device_list:
                row = [
                    Paragraph(device.get('serial_number', '-'), self.table_cell_style),
                    Paragraph(device.get('area_name', '-'), self.table_cell_style),
                    Paragraph(str(device.get('observation_count', 0)), self.table_cell_style),
                    Paragraph(str(device.get('species_count', 0)), self.table_cell_style),
                ]
                table_data.append(row)
            
            device_table = Table(table_data, colWidths=[4*cm, 5*cm, 3*cm, 3*cm])
            device_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            
            story.append(device_table)
        else:
            story.append(Paragraph("暂无设备统计数据", self.body_style))
    
    def _get_conservation_color(self, status):
        """获取保护级别对应的颜色"""
        color_map = {
            'CR': '#dc3545',  # 极危 - 红色
            'EN': '#e74c3c',  # 濒危 - 深红
            'VU': '#f39c12',  # 易危 - 橙色
            'NT': '#17a2b8',  # 近危 - 青色
            'LC': '#28a745',  # 无危 - 绿色
        }
        return color_map.get(status, '#6c757d')


# 便捷函数
def generate_monitoring_report(report_data, output_path=None):
    """
    生成监测报告的便捷函数
    
    Args:
        report_data: 报告数据
        output_path: 输出路径
    
    Returns:
        PDF文件路径或字节流
    """
    generator = ReportGenerator()
    return generator.generate_report(report_data, output_path)
