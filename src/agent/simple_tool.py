


def render_table_tool(columns: list, data: list, title: str = None) -> dict:
    """渲染表格
    
    Args:
        columns (list): 表格列名
        data (list): 表格数据
        title (str, optional): 表格标题. Defaults to None.
        
    Returns:
        dict: 表格数据协议
    """
    return {
        "type": "table",
        "data": data,
        "meta": {
            "title": title
        }
    }