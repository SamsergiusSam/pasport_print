from techData.tech_data import techData


from pypdf import PdfReader, PdfWriter


# Открываем PDF
reader = PdfReader("base_passport.pdf")
writer = PdfWriter()

# Копируем первую страницу
page = reader.pages[0]
writer.add_page(page)

# Заполняем поля
writer.update_page_form_field_values(
    page,
    {
        "type": "G4",
        "qMin": "0,004"
    }
)

# Сохраняем
with open("filled.pdf", "wb") as output_stream:
    writer.write(output_stream)
