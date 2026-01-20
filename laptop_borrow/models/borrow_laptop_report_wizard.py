from odoo import models, fields, api
from datetime import datetime, time
import io
import base64
import xlsxwriter

class BorrowLaptopReportWizard(models.TransientModel):
    _name = 'borrow.laptop.report.wizard'
    _description = 'Wizard Laporan Peminjaman'

    date_from = fields.Date(string="Dari Tanggal", required=True)
    date_to = fields.Date(string="Sampai Tanggal", required=True)

    excel_file = fields.Binary("File Excel", readonly=True)
    file_name = fields.Char("Nama File", readonly=True)

    def action_print_report(self):
        self.ensure_one()

        date_from_dt = datetime.combine(self.date_from, time.min)
        date_to_dt = datetime.combine(self.date_to, time.max)

        domain = [
            ('borrow_date', '>=', date_from_dt),
            ('borrow_date', '<=', date_to_dt),
        ]

        records = self.env['borrow.laptop'].search(domain)

        if not records:
            return {'type': 'ir.actions.act_window_close'}

        return self.env.ref(
            'laptop_borrow.action_report_borrow_laptop'
        ).report_action(records)
        

    def action_export_excel(self):
        self.ensure_one()
        date_from_dt = datetime.combine(self.date_from, time.min)
        date_to_dt = datetime.combine(self.date_to, time.max)

        records = self.env['borrow.laptop'].search([
            ('borrow_date', '>=', date_from_dt),
            ('borrow_date', '<=', date_to_dt),
        ])

        if not records:
            return {'type': 'ir.actions.act_window_close'}

        # Buat file Excel di memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Laporan Peminjaman")

        # format judul
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
        sheet.merge_range('A1:M1', 'LAPORAN PEMINJAMAN BARANG', title_format)

        # format header
        header_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        cell_format = workbook.add_format({'border': 1, 'valign': 'top'})

        headers = ['No','Kode','Tanggal','Tingkat','Jurusan','Kelas','Peminjam',
                'Barang','Jumlah','Tujuan','Guru Mapel','Keterangan','Status']

        # tulis header mulai row ke-2 (index 1)
        for col, header in enumerate(headers):
            sheet.write(1, col, header, header_format)

        # atur lebar kolom agar lebih enak dibaca
        col_widths = [5, 15, 20, 15, 20, 10, 20, 20, 10, 15, 20, 25, 15]
        for i, width in enumerate(col_widths):
            sheet.set_column(i, i, width)

        # tulis data mulai row ke-3 (index 2)
        for row_idx, record in enumerate(records, start=2):
            sheet.write(row_idx, 0, row_idx-1, cell_format)
            sheet.write(row_idx, 1, record.name, cell_format)
            sheet.write(row_idx, 2, record.borrow_date.strftime('%Y-%m-%d %H:%M') if record.borrow_date else '', cell_format)
            sheet.write(row_idx, 3, record.tingkat_id.name if record.tingkat_id else '', cell_format)
            sheet.write(row_idx, 4, record.jurusan_id.name if record.jurusan_id else '', cell_format)
            sheet.write(row_idx, 5, record.class_id.name if record.class_id else '', cell_format)
            sheet.write(row_idx, 6, record.borrower_id.name if record.borrower_id else '', cell_format)
            sheet.write(row_idx, 7, record.product_tmpl_id.name if record.product_tmpl_id else '', cell_format)
            sheet.write(row_idx, 8, record.jumlah_pinjam or 0, cell_format)
            sheet.write(row_idx, 9, record.tujuan_peminjaman or '', cell_format)
            sheet.write(row_idx, 10, record.guru_mapel or '', cell_format)
            sheet.write(row_idx, 11, record.keterangan or '', cell_format)
            sheet.write(row_idx, 12, record.status or '', cell_format)

        workbook.close()
        output.seek(0)

        # encode ke base64
        self.excel_file = base64.b64encode(output.read())
        self.file_name = f"Laporan_Peminjaman_{self.date_from}_s.d_{self.date_to}.xlsx"

        # buka kembali wizard biar bisa download
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'borrow.laptop.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }