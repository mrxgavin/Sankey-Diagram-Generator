import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sankey Diagram Generator",
    page_icon='📈',
    layout="centered",
    initial_sidebar_state="expanded"
)
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Define the function to create Sankey diagram
# 增加 link_opacity 参数
def create_sankey_diagram(
    gene_orders,
    font_size=10,
    colors=None,
    width=1000,
    height=600,
    show_labels=True,
    link_opacity=0.8
):
    columns = len(gene_orders)
    nodes_per_column = max(len(order) for order in gene_orders)

    if colors is None:
        colors = [
            "#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b",
            "#bdcf32", "#87bc45", "#27aeef", "#b33dc6", "#50e991"
        ]
    genes = list(set(gene for order in gene_orders for gene in order))
    color_map = {gene: colors[i % len(colors)] for i, gene in enumerate(genes)}

    # 把 hex 颜色转成带透明度的 rgba 字符串
    def hex_to_rgba(hex_color, opacity):
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{opacity})"

    def get_node_positions(order, x_position):
        if nodes_per_column == 1:
            y_positions = [0.5]
        else:
            y_positions = [0.02 + i * (0.96 / (nodes_per_column - 1)) for i in range(nodes_per_column)]
        return {target: {"x": x_position, "y": y_positions[i]} for i, target in enumerate(order)}

    positions = []
    for i, order in enumerate(gene_orders):
        x_position = 0.05 + i * (0.90 / (columns - 1))
        positions.append(get_node_positions(order, x_position))

    nodes = [gene for order in gene_orders for gene in order]
    node_x = []
    node_y = []
    node_color = []

    for pos in positions:
        for node in pos.keys():
            node_x.append(pos[node]["x"])
            node_y.append(pos[node]["y"])
            node_color.append(color_map[node])

    source = []
    target = []
    value = []
    link_color = []

    for col_idx in range(columns - 1):
        for gene in gene_orders[col_idx]:
            if gene in gene_orders[col_idx + 1]:
                source_idx = col_idx * nodes_per_column + gene_orders[col_idx].index(gene)
                target_idx = (col_idx + 1) * nodes_per_column + gene_orders[col_idx + 1].index(gene)

                source.append(source_idx)
                target.append(target_idx)
                value.append(1)
                # 使用带透明度的颜色
                link_color.append(hex_to_rgba(color_map[gene], link_opacity))
            else:
                continue
    
    # 根据 show_labels 决定标签内容
    node_labels = [f"{n}" for n in nodes] if show_labels else ["" for _ in nodes]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            # 去掉外框线
            line=dict(color="black", width=0),
            label=node_labels,
            color=node_color,
            x=node_x,
            y=node_y
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_color
        )
    )])

    fig.update_traces(
        textfont_family="Arial, Helvetica, sans-serif",
        textfont_size=font_size,
        textfont_color="black",
        textfont_shadow="none",   # 关键：去掉那一圈描边
        selector=dict(type="sankey")
    )

    fig.update_layout(
        title_text="",
        font_size=font_size,
        autosize=True,
        width=width,
        height=height
    )

    for i in range(columns):
        x_position = 0.05 + i * (0.90 / (columns - 1))
        fig.add_annotation(
            x=x_position,
            y=1.1,
            text=f"Cell {i+1}",
            showarrow=False,
            font_size=font_size + 4
        )

    return fig


# MATLAB 代码生成函数（保持不变，不使用透明度）
def generate_matlab_code(gene_orders, colors=None, show_labels=True):
    if colors is None:
        colors = [
            "#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b",
            "#bdcf32", "#87bc45", "#27aeef", "#b33dc6", "#50e991"
        ]
    genes = list(set(gene for order in gene_orders for gene in order))
    color_map = {gene: colors[i % len(colors)] for i, gene in enumerate(genes)}
    
    columns = len(gene_orders)
    nodes_per_column = max(len(order) for order in gene_orders)
    
    box_width = 0.3
    box_height = 0.6
    max_line_width = 4
    
    matlab_code = []
    
    matlab_code.append("figure; hold on;")
    
    def bezier_curve(x1, y1, x2, y2, width, color):
        matlab_code.append(f"x = linspace({x1}, {x2}, 100);")
        matlab_code.append(f"y = {y1} + ({y2} - {y1}) * (1 - cos(pi * (x - {x1}) / ({x2} - {x1}))) / 2;")
        matlab_code.append(f"w = linspace({width}, {width / 2}, 100);")
        matlab_code.append("for i = 1:length(x)-1")
        matlab_code.append(f"    plot(x(i:i+1), y(i:i+1), 'Color', '{color}', 'LineWidth', w(i));")
        matlab_code.append("end")
    
    # Plot the connections first so that they are behind the boxes
    for col_idx in range(columns - 1):
        for gene in gene_orders[col_idx]:
            if gene in gene_orders[col_idx + 1]:
                source_idx = nodes_per_column - gene_orders[col_idx].index(gene)
                target_idx = nodes_per_column - gene_orders[col_idx + 1].index(gene)
                line_color = color_map[gene]
                source_x = col_idx + box_width / 2
                target_x = col_idx + 1 - box_width / 2
                bezier_curve(source_x, source_idx, target_x, target_idx, max_line_width, line_color)
    
    # Plot the boxes and labels on top
    for col_idx, order in enumerate(gene_orders):
        for node_idx, gene in enumerate(order):
            color = color_map[gene]
            y_position = nodes_per_column - node_idx
            matlab_code.append(
                f"rectangle('Position', [{col_idx - box_width/2}, {y_position - box_height/2}, "
                f"{box_width}, {box_height}], 'FaceColor', '{color}', 'EdgeColor', '{color}', 'LineWidth', 1.5);"
            )
            
            if show_labels:
                matlab_code.append(
                    f"text({col_idx}, {y_position}, '{gene}', 'Color', 'k', 'FontWeight', 'bold', "
                    f"'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');"
                )
    
    col_labels = ['Cell ' + str(i + 1) for i in range(columns)]
    col_labels_str = ', '.join(f"'{label}'" for label in col_labels)
    matlab_code.append(f"set(gca, 'XTick', 0:{columns - 1}, 'XTickLabel', {{{col_labels_str}}}, 'YTick', []);")
    matlab_code.append("title('Sankey Diagram');")
    matlab_code.append("xlim([-0.5, {}]);".format(columns - 0.5))
    matlab_code.append("ylim([-1, {}]);".format(nodes_per_column + 1))
    matlab_code.append("hold off;")
    
    return "\n".join(matlab_code)



########################################################################
########################################################################
########################################################################
########################################################################
# Streamlit app
st.title("Sankey Diagram Generator")

st.sidebar.header("Configuration")
columns = st.sidebar.number_input("Number of Columns", min_value=2, max_value=8, value=3)

default_gene_orders = [
    ["MYC", "CDK2", "AKT", "PI3K", "PDK1", "INSR", "GSK3B", "MTORC1", "CDK46", "MEK"],
    ["MYC", "CDK2", "PI3K", "AKT", "GSK3B", "PDK1", "INSR", "MTORC1", "CDK46", "MEK"],
    ["MYC", "CDK2", "AKT", "PI3K", "GSK3B", "PDK1", "MTORC1", "INSR", "MEK", "CDK46"],
    ["MEK", "GSK3B", "PDK1", "CDK46", "MYC", "CDK2", "PI3K", "AKT", "MTORC1", "INSR"],
    ["PDK1", "MEK", "AKT", "CDK46", "GSK3B", "INSR", "CDK2", "MTORC1", "MYC", "PI3K"],
    ["MTORC1", "INSR", "MYC", "GSK3B", "PI3K", "PDK1", "AKT", "CDK2", "CDK46", "MEK"],
    ["AKT", "MYC", "CDK46", "MEK", "PI3K", "CDK2", "PDK1", "MTORC1", "INSR", "GSK3B"],
    ["PI3K", "PDK1", "INSR", "CDK2", "MTORC1", "AKT", "GSK3B", "MEK", "CDK46", "MYC"]
]

gene_orders = []
for i in range(columns):
    gene_order = st.sidebar.text_area(
        f"Gene Order for Cell {i+1}",
        value=" ".join(default_gene_orders[i]),
        height=100
    )
    gene_orders.append(gene_order.split())

advanced_settings = st.sidebar.expander("Advanced Settings", expanded=False)
with advanced_settings:
    font_size = st.slider("Font Size", min_value=5, max_value=50, value=15)
    width = st.slider("Diagram Width", min_value=300, max_value=1600, value=1000)
    height = st.slider("Diagram Height", min_value=300, max_value=6000, value=600)
    link_opacity = st.slider(
        "Link Opacity",
        min_value=0.1,
        max_value=1.0,
        value=0.8,
        step=0.05
    )
    show_labels = st.checkbox("Show Node Labels", value=False)

if st.sidebar.button("Generate Diagram"):
    # 传递 link_opacity 参数
    fig = create_sankey_diagram(
        gene_orders,
        font_size=font_size,
        width=width,
        height=height,
        show_labels=show_labels,
        link_opacity=link_opacity
    )
    st.plotly_chart(fig, use_container_width=True)

    # Downloadable Python source code（也包含 link_opacity 参数）
    source_code = f'''
import plotly.graph_objects as go

def create_sankey_diagram(
    gene_orders,
    font_size=10,
    colors=None,
    width=1000,
    height=600,
    show_labels=True,
    link_opacity=0.8
):
    columns = len(gene_orders)
    nodes_per_column = max(len(order) for order in gene_orders)

    if colors is None:
        colors = ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b",
                  "#bdcf32", "#87bc45", "#27aeef", "#b33dc6", "#50e991"]
    genes = list(set(gene for order in gene_orders for gene in order))
    color_map = {{gene: colors[i % len(colors)] for i, gene in enumerate(genes)}}

    def hex_to_rgba(hex_color, opacity):
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({{r}},{{g}},{{b}},{{opacity}})"

    def get_node_positions(order, x_position):
        if nodes_per_column == 1:
            y_positions = [0.5]
        else:
            y_positions = [0.02 + i * (0.96 / (nodes_per_column - 1)) for i in range(nodes_per_column)]
        return {{target: {{"x": x_position, "y": y_positions[i]}} for i, target in enumerate(order)}}

    positions = []
    for i, order in enumerate(gene_orders):
        x_position = 0.05 + i * (0.90 / (columns - 1))
        positions.append(get_node_positions(order, x_position))

    nodes = [gene for order in gene_orders for gene in order]
    node_x = []
    node_y = []
    node_color = []

    for pos in positions:
        for node in pos.keys():
            node_x.append(pos[node]["x"])
            node_y.append(pos[node]["y"])
            node_color.append(color_map[node])

    source = []
    target = []
    value = []
    link_color = []

    for col_idx in range(columns - 1):
        for gene in gene_orders[col_idx]:
            if gene in gene_orders[col_idx + 1]:
                source_idx = col_idx * nodes_per_column + gene_orders[col_idx].index(gene)
                target_idx = (col_idx + 1) * nodes_per_column + gene_orders[col_idx + 1].index(gene)
                source.append(source_idx)
                target.append(target_idx)
                value.append(1)
                link_color.append(hex_to_rgba(color_map[gene], link_opacity))

    node_labels = [f'{{n}}' for n in nodes] if show_labels else ["" for _ in nodes]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0),
            label=node_labels,
            color=node_color,
            x=node_x,
            y=node_y
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_color
        )
    )])

    fig.update_layout(
        title_text="",
        font_size=font_size,
        autosize=True,
        width=width,
        height=height
    )

    for i in range(columns):
        x_position = 0.05 + i * (0.90 / (columns - 1))
        fig.add_annotation(x=x_position, y=1.1, text=f"Cell {{i+1}}", showarrow=False, font_size=font_size + 4)

    return fig

gene_orders = {gene_orders}

# Generating diagram
create_sankey_diagram(
    gene_orders,
    font_size={font_size},
    width={width},
    height={height},
    show_labels={show_labels},
    link_opacity={link_opacity}
)
'''
    st.download_button("Download Python Code", data=source_code, file_name="sankey_diagram.py", mime="text/plain")

    matlab_code = generate_matlab_code(gene_orders, show_labels=show_labels)
    st.download_button("Download MATLAB Code", data=matlab_code, file_name="sankey_diagram.m", mime="text/plain")
