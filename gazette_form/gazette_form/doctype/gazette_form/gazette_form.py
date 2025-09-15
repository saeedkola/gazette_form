# Copyright (c) 2024, Humaid and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from io import BytesIO
from pypdf import PdfReader, PdfWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter,A4
from reportlab.lib.units import cm
import io


def format_aadhaar_number(aadhaar_number):
    aadhaar_str = str(aadhaar_number)
    formatted_aadhaar = ' '.join([aadhaar_str[i:i+4] for i in range(0, len(aadhaar_str), 4)])
    return formatted_aadhaar


class GazetteForm(Document):
	def validate(self,method=None):
		if not self.aadhaar_number.isnumeric() or len(self.aadhaar_number) != 12:
			frappe.throw("Aadhaar Number Not valid")
			


@frappe.whitelist()
def export_pdf(gazette_form):
	file= frappe.get_doc("File",{
		"file_name": "gazette_form_template.pdf"
	})
	pdf_template_path = file.get_full_path() 
	
	existing_pdf = PdfReader(pdf_template_path)

	
	# Create a PDF with the added text using ReportLab
	packet = io.BytesIO()
	can = canvas.Canvas(packet, pagesize=A4)
	form_data = frappe.get_doc("Gazette Form",gazette_form)
	start_y = 24.85
	pitch = 0.84

	formatted_aadhaar = format_aadhaar_number(form_data.aadhaar_number)
	
	can.drawString(5 * cm, (start_y - pitch * 0) * cm, formatted_aadhaar)
	can.drawString(5* cm, (start_y - pitch *1) * cm, form_data.full_name)
	if form_data.co:
		can.drawString(5* cm,  (start_y - pitch *3) * cm, form_data.co)
	if form_data.house_number:
		can.drawString(5* cm,  (start_y - pitch *4) * cm, form_data.house_number)
	if form_data.street:
		can.drawString(5* cm,  (start_y - pitch *5) * cm, form_data.street)
	if form_data.landmark:
		can.drawString(5* cm, (start_y - pitch *6) * cm, form_data.landmark)
	if form_data.arealocality:
		can.drawString(5* cm,  (start_y - pitch *7) * cm, form_data.arealocality)
	can.drawString(5* cm,  (start_y - pitch *8) * cm, form_data.villagetown)
	can.drawString(5* cm,  (start_y - pitch *9) * cm, form_data.post_office)
	can.drawString(5* cm,  (start_y - pitch *10) * cm, form_data.district)
	can.drawString(5* cm,  (start_y - pitch *11) * cm, form_data.state)
	can.drawString(5* cm, 13.55 * cm, form_data.pin_code)
	can.drawString(5* cm, 12.50 * cm, form_data.dob.strftime("%d"))
	can.drawString(6.7* cm, 12.50 * cm, form_data.dob.strftime("%m"))
	can.drawString(8.5* cm, 12.50 * cm, form_data.dob.strftime("%Y"))

	from datetime import date

	today = date.today()
	can.drawString(14.5* cm, (start_y+2.5) * cm, today.strftime("%d"))
	can.drawString(16.2* cm, (start_y+2.5) * cm, today.strftime("%m"))
	can.drawString(18.2* cm, (start_y + 2.5) * cm, today.strftime("%Y"))
	if form_data.resident:
		can.drawString(4.8* cm, (start_y + pitch) * cm, "✓")
	if form_data.nri:
		can.drawString((4.8 +3.2)* cm, (start_y + pitch) * cm, "✓")
	if form_data.new_enrollment:
		can.drawString((4.8 +8.7)* cm, (start_y + pitch) * cm, "✓")
	if form_data.update_aadhaar:
		can.drawString((4.8 +12.6)* cm, (start_y + pitch) * cm, "✓")


	can.save()

	packet.seek(0)

	# Read the new PDF
	new_pdf = PdfReader(packet)
	output_pdf = PdfWriter()
	page = existing_pdf.pages[0]
	page.merge_page(new_pdf.pages[0])
	output_pdf.add_page(page)

	pdf_file = BytesIO()

	output_pdf.write(pdf_file)
	pdf_file.seek(0)
	frappe.local.response.filename = "{} - {}.pdf".format(form_data.full_name,form_data.aadhaar_number)
	frappe.local.response.filecontent = pdf_file.read()
	frappe.local.response.type = "download"

	
