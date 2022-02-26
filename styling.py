def datatable_styling(*headers,text_align='center', width='30%'):
    style_cell_conditional = [
        {
            'if': {'column_id': c},
            'textAlign':text_align,
            'width': width,
        } for c in headers
    ]
    return style_cell_conditional
