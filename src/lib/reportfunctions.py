import logging
from collections import OrderedDict
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import LETTER, inch
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle

import src.lib.helpers.helpers as helpers
import src.lib.sqlfunctions as sql_functions


class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []
        self.width, self.height = LETTER

    def showPage(self):
        self.pages.append(dict(super().__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            super().__dict__.update(page)
            if self._pageNumber > 1:
                self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        page = f"Page {self._pageNumber} of {page_count}"
        x = 128
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        self.drawImage("src/lib/asset/Logo.png",
                       self.width - inch * 2,
                       self.height - 50,
                       width=100,
                       height=30,
                       preserveAspectRatio=True,
                       mask='auto'
                       )
        self.line(30, 740, LETTER[0] - 50, 740)
        self.line(66, 78, LETTER[0] - 66, 78)
        self.setFont('Times-Roman', 10)
        self.drawString(LETTER[0] - x, 65, page)
        self.restoreState()


class PDFPSReport:
    """
    This class will generate and save a PDF copy of a company's risk assessment when called.
    :param _id:    uuid of the company whose assessment is to be converted to a PDF report.
    :type _id:     str
    :param path:   path where the PDF will be saved.
    :type path:    str
    """
    def __init__(self, _id, path):
        self.path = path
        self._id = _id
        self.data = self.get_data()
        self.colors = self.get_colors()
        self.stylesheet = self.get_stylesheet()
        self.table_styles = self.get_table_styles()
        self.elements = self.get_elements()

        # Build the PDF
        self.doc = SimpleDocTemplate(path, pagesize=LETTER)
        self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

    @staticmethod
    def get_colors():
        """
        Store the colours that will be used in the PDF here.
        """
        # colors - Azul turkeza 367AB3
        colors = {"colorOhkaGreen0": Color((45.0 / 255), (166.0 / 255), (153.0 / 255), 1),
                  "colorOhkaGreen1": Color((182.0 / 255), (227.0 / 255), (166.0 / 255), 1),
                  "colorOhkaGreen2": Color((140.0 / 255), (222.0 / 255), (192.0 / 255), 1),
                  "colorOhkaBlue0": Color((35.0 / 255), (48.0 / 255), (68.0 / 255), 1),
                  "colorOhkaBlue1": Color((35.0 / 255), (48.0 / 255), (68.0 / 255), 1),
                  "colorOhkaGreenLines": Color((50.0 / 255), (140.0 / 255), (140.0 / 255), 1),
                  }
        return colors

    def get_stylesheet(self):
        """
        Store the styles that will be used in the PDF here so they can be easily referenced throughout the document.
        """
        stylesheet = StyleSheet1()
        stylesheet.add(ParagraphStyle('Heading3',
                                      fontSize=12,
                                      leading=14,
                                      justifyBreaks=1,
                                      alignment=TA_LEFT,
                                      justifyLastLine=1,
                                      ),
                       alias='h3')
        stylesheet.add(ParagraphStyle('SectionHeader',
                                      fontSize=12,
                                      alignment=TA_LEFT,
                                      borderWidth=3,
                                      textColor=self.colors["colorOhkaBlue0"],
                                      spaceBefore=12,
                                      spaceAfter=6,
                                      ),
                       alias='section')
        stylesheet.add(ParagraphStyle('Normal',
                                      fontSize=10,
                                      leading=14,
                                      justifyBreaks=1,
                                      alignment=TA_LEFT,
                                      justifyLastLine=1,
                                      spaceBefore=6
                                      ),
                       alias='normal'),
        stylesheet.add(ParagraphStyle('Table Header',
                                      fontSize=8,
                                      alignment=TA_CENTER,
                                      ),
                       alias='table-header'),
        stylesheet.add(ParagraphStyle('Table Text',
                                      fontSize=8
                                      ),
                       alias='table-text'),
        return stylesheet

    def get_table_styles(self):
        """
        Store generic table styles here. If specific styles are needed for each table column, create new temporary
        paragraph styles in the section itself.
        """
        t_style = {"normal": TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                         ("FONTSIZE", (0, 0), (-1, -1), 8),
                                         ('LINEABOVE', (0, 0), (-1, -1), 1, self.colors["colorOhkaBlue1"]),
                                         ('BACKGROUND', (0, 0), (-1, 0), self.colors["colorOhkaGreenLines"]),
                                         ]
                                        )
                   }
        return t_style

    def get_data(self):
        """
        Retrieve the required data to be displayed in the PDF from the database.
        """
        logging.info("Retrieving data form db....")
        connection = sql_functions.make_connection()

        # Write string queries
        company_details_query = """
        SELECT ic.id, ic.name, ic.assessment_progress, ic.last_assessed_at,
        ic.threat_assessment_status, ic.scan_status, ic.control_status, ic.scan_results,
        ic.application_datetime FROM company ic where ic.id = %s
        """
        financials_query = """
        SELECT company_id, risk, threat_category_losses FROM financial where company_id = %s
        """

        query_fields = (self._id,)
        logging.info(f"Company UUID: {self._id}")
        company_details_data = sql_functions.retrieve_rows_safe(connection, company_details_query, query_fields)
        financials_data = sql_functions.retrieve_rows_safe(connection, financials_query, query_fields)
        financials_key = ('uuid', 'risk', 'threatCategory')
        financials_result = []
        for row in financials_data:
            financials_result.append(dict(zip(financials_key, row)))

        company_details_key = ('id', 'companyName', 'assessmentProgress', 'lastAssessed',
                               'threatAssessment', 'exposureAssessment', 'controlsAssessment', 'scanResults',
                               'applicationDatetime',
                               )
        data = dict()
        for row in company_details_data:
            data = dict(zip(company_details_key, row))
            data['financials'] = financials_result[0]

        # Restructure the scan results data to allow for easy retrieval of data later
        data['scanResults']['data'] = helpers.filter_scan_info(data['scanResults']['data'])
        data['scanResults'] = helpers.get_pdf_data(data['scanResults'])

        # Convert application datetime to correct format
        data["applicationDatetime"] = data["applicationDatetime"].strftime("%d %b %Y")

        logging.debug(f"Retrieved data:\n{data}")
        return data

    def get_cover_page(self):
        """
        Returns a list of elements that will form the cover page of the PDF.
        """
        logging.info("Creating cover page....")
        elements = []
        img = Image("src/lib/asset/Logo.png")
        img.drawHeight = 4 * inch
        img.drawWidth = 4.5 * inch
        elements.append(img)

        spacer = Spacer(10, 250)
        elements.append(spacer)

        text = (f"PROTOS LABS RISK ASSESSMENT REPORT<br/>"
                f"Client: {self.data['companyName']}<br/>"
                f"Date: {self.data['applicationDatetime']}<br/>"
                )
        paragraph_report_summary = Paragraph(text, self.stylesheet["h3"])
        elements.append(paragraph_report_summary)
        elements.append(PageBreak())

        return elements

    def get_overview(self):
        """
        Returns a list of elements that will form the overview section of the PDF.
        """
        logging.info("Creating overview....")
        elements = []
        text = 'OVERVIEW'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)
        text = (f"This report summarizes the findings and recommendations of Protos Labs’ cyber risk assessment "
                f"conducted on {self.data['applicationDatetime']}."
                )
        overview_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(overview_content)

        return elements

    def get_assessment_scope(self):
        """
        Returns a list of elements that will form the scope of assessment section of the PDF.
        """
        logging.info("Creating scope of assessment....")
        elements = []
        text = 'SCOPE OF ASSESSMENT'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)
        text = ("The risk assessment was conducted on your organization’s digital assets in the public domain across "
                "six (6) key areas as follows:<br/>"
                "1.  Email Security,<br/>"
                "2.  Vulnerabilities,<br/>"
                "3.  Secure Headers,<br/>"
                "4.  Services,<br/>"
                "5.  Leaked Credentials, and<br/>"
                "6.  Marketplace Mentions.<br/><br/>"
                "Detailed descriptions of each area can be found in the appendix.")
        overview_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(overview_content)

        return elements

    def get_methodology(self):
        """
        Returns a list of elements that will form the methodology section of the PDF.
        """
        logging.info("Creating methodology....")
        elements = []
        text = 'METHODOLOGY'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        text = ("Protos Labs leverages advanced scanning and collection techniques, similar to those used by bad "
                "actors, to assess your organization’s cybersecurity posture from the open and dark web. "
                "These techniques rely solely on information found in the public domain and do not access any of "
                "your organization’s private resources or assets.<br/><br/>We combine the results of the scans with "
                "real-world historical breach data and advanced machine learning models to estimate the overall cyber "
                "risk exposure of your organization in monetary terms. "
                )
        overview_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(overview_content)

        return elements

    def get_overall_risk_exposure(self):
        """
        Returns a list of elements that will form the overall risk exposure section of the PDF.
        """
        logging.info("Creating overall risk exposure page....")
        elements = [PageBreak()]
        text = 'OVERALL RISK EXPOSURE'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        text = (f"The overall cyber risk exposure of your organization is estimated at "
                f"<u>${'{:,}'.format(int(self.data['financials']['risk']))}.</u><br/><br/>"
                f"This loss magnitude figure is derived from estimating the financial impact of the top six (6) cyber "
                f"threats that are relevant to your organization. Details of the loss estimates for each threat "
                f"category is found in the table below. The estimates are computed from data from peer companies, "
                f"your company’s cyber posture and real-world historical cyber incidents."
                )
        overview_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(overview_content)

        spacer = Spacer(10, 15)
        elements.append(spacer)

        """
        Create table
        """
        table_data = []  # Will be a 2D list with each sublist corresponding to 1 row in the table.

        # Create table headers
        cols = OrderedDict([("<b>No.</b>", ParagraphStyle(name="01",
                                                          parent=self.stylesheet["table-text"],
                                                          alignment=TA_CENTER
                                                          )),
                            ("<b>Risk</b>", ParagraphStyle(name="02",
                                                           parent=self.stylesheet["table-text"],
                                                           alignment=TA_CENTER
                                                           )),
                            ("<b>Description</b>", ParagraphStyle(name="03",
                                                                  parent=self.stylesheet["table-text"],
                                                                  alignment=TA_LEFT
                                                                  )),
                            ("<b>Exposure ($)</b>", ParagraphStyle(name="04",
                                                                   parent=self.stylesheet["table-text"],
                                                                   alignment=TA_CENTER
                                                                   )),
                            ])
        table_headers = [Paragraph(table_header, self.stylesheet["table-header"]) for table_header in cols.keys()]
        table_data.append(table_headers)

        # Add table data
        threat_category_data = self.data["financials"]["threatCategory"]["data"]
        for line_num, raw_line_data in enumerate(threat_category_data):
            line_data = [str(line_num + 1),
                         raw_line_data["threatCategory"],
                         "Description",
                         '{:,}'.format(raw_line_data["risk"]),
                         ]
            formatted_line_data = [Paragraph(item, item_style) for item, item_style in zip(line_data, cols.values())]
            table_data.append(formatted_line_data)

        # Create table flowable
        table = Table(table_data, colWidths=[50, 100, 200, 100])
        table.setStyle(self.table_styles["normal"])
        elements.append(table)

        return elements

    def get_findings_and_recommendations(self):
        """
        Returns a list of elements that will form the findings and recommendations section of the PDF.
        """
        logging.info("Creating findings and recommendations page....")
        elements = [PageBreak()]
        text = 'FINDINGS AND RECOMMENDATIONS'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        text = ("The findings of this report are categorized into three risk levels. High, Medium, and Low.<br/>"
                "•   High risks describe issues that could be immediately used by bad actors to conduct attacks on "
                "your organization.<br/>"
                "•   Medium risks describe issues that your organization should keep track of and a make decision to "
                "close or not.<br/>"
                "•   Low risks means that Protos Labs has found no current issues.<br/>"
                )
        overview_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(overview_content)

        spacer = Spacer(10, 15)
        elements.append(spacer)

        """
        Create table
        """
        table_data = []  # Will be a 2D list with each sublist corresponding to 1 row in the table.

        # Create table headers
        cols = OrderedDict([("<b>No</b>.", ParagraphStyle(name="01",
                                                          parent=self.stylesheet["table-text"],
                                                          alignment=TA_CENTER
                                                          )),
                            ("<b>Finding</b>", ParagraphStyle(name="02",
                                                              parent=self.stylesheet["table-text"],
                                                              alignment=TA_LEFT
                                                              )),
                            ("<b>Risk Area</b>", ParagraphStyle(name="03",
                                                                parent=self.stylesheet["table-text"],
                                                                alignment=TA_CENTER
                                                                )),
                            ("<b>Risk Level</b>", ParagraphStyle(name="04",
                                                                 parent=self.stylesheet["table-text"],
                                                                 alignment=TA_CENTER
                                                                 )),
                            ("<b>Recommendations</b>", ParagraphStyle(name="05",
                                                                      parent=self.stylesheet["table-text"],
                                                                      alignment=TA_LEFT
                                                                      )),
                            ])
        table_headers = [Paragraph(table_header, self.stylesheet["table-header"]) for table_header in cols.keys()]
        table_data.append(table_headers)

        # Add table data
        for row in self.data["scanResults"]:
            line_data = [str(row["idx"]), row["finding"], row["area"], row["level"], row["rec"]]
            formatted_line_data = [Paragraph(item, item_style) for item, item_style in zip(line_data, cols.values())]
            table_data.append(formatted_line_data)

        # Create table flowable
        table = Table(table_data, colWidths=[30, 60, 120, 60, 170])
        table.setStyle(self.table_styles["normal"])
        elements.append(table)

        return elements

    def get_appendix(self):
        """
        Returns a list of elements that will form the appendix section of the PDF.
        """
        logging.info("Creating appendix....")
        elements = [PageBreak()]
        text = 'APPENDIX'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        text = ("<b>Definitions:</b><br/><br/>"
                "<b>Cyber Risk Exposure:</b> Your annual cyber risk exposure is assessed based on their security "
                "defenses in the public domain, real-world historical data and expert analysis.<br/><br/>"
                "<b>Leaked Credentials:</b> Protos Labs has scanned the dark web for leaked credentials associated to "
                "your organization that can be used by threat actors to launch attacks.<br/><br/>"
                "<b>Email Security:</b> Protos Labs has checked your email security to assess whether they are "
                "susceptible to phishing attacks and email spam.<br/><br/>"
                "<b>Marketplace Mentions:</b> Protos Labs has searched underground cybercriminal forums to check if "
                "your data or network access is being sold.<br/><br/>"
                "<b>Vulnerabilities:</b> Protos Labs has scanned your public facing assets to assess for "
                "vulnerabilities that threat actors can exploit.<br/><br/>"
                "<b>Services:</b> Protos Labs has scanned your public facing assets to assess for services that can "
                "be exploited by threat actors to conduct cyber attacks.<br/><br/>")
        overview_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(overview_content)

        return elements

    def get_elements(self):
        """
        Stitch all elements from each section into one single list of elements that will be rendered.
        """
        sections = (self.get_cover_page(),
                    self.get_overview(),
                    self.get_assessment_scope(),
                    self.get_methodology(),
                    self.get_overall_risk_exposure(),
                    self.get_findings_and_recommendations(),
                    self.get_appendix(),
                    )
        elements = [element for section in sections for element in section]

        return elements
