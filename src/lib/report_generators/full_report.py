import logging
from collections import OrderedDict
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import LETTER, inch, landscape
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle, ListItem, \
    ListFlowable, Frame, PageTemplate, NextPageTemplate
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from src.lib.report_generators.raw_data import industry2info, industry2landscape, industry2ref, \
    applnindustry2rptindustry

import src.lib.helpers.helpers as helpers
import src.lib.report_generators.report_helpers as report_helpers
import src.lib.sqlfunctions as sql_functions

# Variables
prepared_by = "Gilbert Choo, Lead of Cyber Engagement"
email = "gilbert_choo@protoslabs.sg"
mobile = "+65 8129 8114"


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
            if self._pageNumber == 1:
                self.draw_image_cover()
            if self._pageNumber > 1:
                self.draw_canvas_header(page_count)
                self.draw_canvas_footer()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas_header(self, page_count):
        page = f"{self._pageNumber}"
        self.saveState()
        self.drawImage("src/lib/asset/header.jpg",
                        518,
                        0,
                        width=100,
                        height=self.height,
                        preserveAspectRatio=True,
                        anchor='nw'
                       )
        self.setFillColorRGB(1, 1, 1)
        self.setFontSize(14)
        self.drawCentredString(7.85 * inch, 10.62 * inch, page)
        self.restoreState()

    def draw_canvas_footer(self):
        self.saveState()
        self.drawImage("src/lib/asset/footer.jpg",
                       0,
                       -5.25 * inch,
                       width=self.width,
                       height=self.height,
                       preserveAspectRatio=True,
                       anchor='c'
                       )
        self.setFillColorRGB(1, 1, 1)
        self.setFontSize(14)
        self.drawCentredString(4.28 * inch, 0.2 * inch, "www.protoslabs.sg")
        self.restoreState()

    def draw_image_cover(self):
        self.drawImage("src/lib/asset/PDF image_full.jpg",
                       67,
                       40,
                       width=self.width,
                       height=450,
                       preserveAspectRatio=True,
                       anchor='se'
                       )
        self.drawImage("src/lib/asset/PL Black Logo.png",
                       3.5 * inch,
                       -4.8 * inch,
                       width=135,
                       height=self.height,
                       preserveAspectRatio=True,
                       anchor='c'
                       )


class FullReport:
    """
    This class will generate and save a PDF copy of a company's full risk assessment when called.
    :param _id:    uuid of the company whose assessment is to be converted to a PDF report.
    :type _id:     str
    :param path:   path where the PDF will be saved.
    :type path:    str
    """

    def __init__(self, _id, path):
        self.path = path
        self._id = _id
        self.industry = "general"
        self.data = self.get_data()
        self.colors = self.get_colors()
        self.stylesheet = self.get_stylesheet()
        self.table_styles = self.get_table_styles()
        self.elements = self.get_elements()

        # Build the PDF
        self.doc = SimpleDocTemplate(path, pagesize=LETTER, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                                     topMargin=0.8 * inch, bottomMargin=0.8 * inch)
        self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

    @staticmethod
    def get_colors():
        """
        Store the colours that will be used in the PDF here.
        """
        # colors - Azul turkeza 367AB3
        colors = {"titleColor": HexColor('#012169'),
                  "tableGridLineColor": HexColor('#000000'),
                  "tableGridBgColor": HexColor('#FFFFFF'),
                  "barChartBarColor": HexColor('#1d7d71'),
                  "barChartStrokeColor": HexColor('#d6dfdc')
                  }
        return colors

    def get_stylesheet(self):
        """
        Store the styles that will be used in the PDF here so they can be easily referenced throughout the document.
        """
        stylesheet = StyleSheet1()
        stylesheet.add(ParagraphStyle('Classification',
                                      fontSize=12,
                                      font="Arial",
                                      justifyBreaks=1,
                                      alignment=TA_CENTER,
                                      justifyLastLine=1,
                                      ),
                       alias='classification')
        stylesheet.add(ParagraphStyle('Title',
                                      fontSize=50,
                                      font="Arial",
                                      textColor=self.colors["titleColor"],
                                      leading=50,
                                      justifyBreaks=1,
                                      alignment=TA_LEFT,
                                      justifyLastLine=1,
                                      ),
                       alias='Title')
        stylesheet.add(ParagraphStyle('Heading3',
                                      fontSize=14,
                                      leading=20,
                                      justifyBreaks=1,
                                      alignment=TA_LEFT,
                                      justifyLastLine=1,
                                      ),
                       alias='h3')
        stylesheet.add(ParagraphStyle('SectionHeader',
                                      fontSize=16,
                                      alignment=TA_LEFT,
                                      borderWidth=3,
                                      leading=20
                                      ),
                       alias='section')
        stylesheet.add(ParagraphStyle('Normal',
                                      fontSize=12,
                                      leading=20,
                                      justifyBreaks=1,
                                      alignment=TA_LEFT,
                                      justifyLastLine=1,
                                      spaceBefore=6
                                      ),
                       alias='normal'),
        stylesheet.add(ParagraphStyle('Note',
                                      fontSize=10,
                                      leading=20,
                                      ),
                       alias='note'),
        stylesheet.add(ParagraphStyle('Table Header',
                                      fontSize=12,
                                      alignment=TA_LEFT,
                                      ),
                       alias='table-header'),
        stylesheet.add(ParagraphStyle('Table Text',
                                      fontSize=12
                                      ),
                       alias='table-text'),
        return stylesheet

    def get_table_styles(self):
        """
        Store generic table styles here. If specific styles are needed for each table column, create new temporary
        paragraph styles in the section itself.
        """
        t_style = {"normal": TableStyle([('GRID', (0, 0), (-1, -1), 0.5, self.colors["tableGridLineColor"]),
                                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                         ("FONTSIZE", (0, 0), (-1, -1), 12),
                                         ('BACKGROUND', (0, 0), (-1, 0), self.colors["tableGridBgColor"]),
                                         ]
                                        )
                   }
        return t_style

    def get_data(self):
        """
        Retrieve the required data to be displayed in the PDF from the database.
        """
        logging.info("Retrieving data from db....")

        connection = sql_functions.make_connection()

        # Write string queries
        company_details_query = ("SELECT ic.id, ic.name, ic.industry, ic.assessment_progress, ic.last_assessed_at, "
                                 "ic.employees, ic.threat_assessment_status, ic.scan_status, ic.control_status, "
                                 "ic.scan_results, ic.application_datetime "
                                 "FROM public.company ic where ic.id = %s"
                                 )
        financials_query = """SELECT company_id, risk, threat_category_losses FROM financial where company_id=%s"""

        query_fields = (self._id,)
        logging.info(f"Company UUID: {self._id}")
        company_details_data = sql_functions.retrieve_rows_safe(connection, company_details_query, query_fields)
        financials_data = sql_functions.retrieve_rows_safe(connection, financials_query, query_fields)
        financials_key = ('uuid', 'risk', 'threatCategory')
        financials_result = []
        for row in financials_data:
            financials_result.append(dict(zip(financials_key, row)))

        company_details_key = ('id', 'companyName', 'industry', 'assessmentProgress', 'lastAssessed', 'employees',
                               'threatAssessment', 'exposureAssessment', 'controlsAssessment', 'scanResults',
                               'applicationDatetime',
                               )
        raw_pdf_data = dict()
        for row in company_details_data:
            raw_pdf_data = dict(zip(company_details_key, row))
            raw_pdf_data['financials'] = financials_result[0]

        # If phishing is present in threat categories, then add it to BEC and delete off
        threat_cats = raw_pdf_data["financials"]["threatCategory"]["data"]
        for threat_cat in threat_cats:
            if threat_cat["threatCategory"].lower() == "phishing":
                phishing_risk = threat_cat["risk"]
                for threat_cat_nest in threat_cats:
                    if threat_cat_nest["threatCategory"].lower() == "business email compromise":
                        threat_cat_nest["risk"] += phishing_risk
                        break
                threat_cats.remove(threat_cat)
                break

        # Restructure the scan results data to allow for easy retrieval of data later
        raw_pdf_data['scanResults']['data'] = helpers.filter_scan_info(raw_pdf_data['scanResults']['data'])
        pdf_data = report_helpers.get_full_pdf_data(raw_pdf_data)

        # Add correct industry to self.industry to generate the correct kind of report
        self.industry = raw_pdf_data["industry"]

        return pdf_data

    def get_cover_page(self):
        """
        Returns a list of elements that will form the cover page of the PDF.
        """
        logging.info("Creating cover page....")
        elements = []

        # Variables
        company = self.data["company"]
        doc_date = self.data["doc_date"]

        spacer_120 = Spacer(0, 120)
        spacer_30 = Spacer(10, 30)

        classification_text = "<b>PRIVATE & CONFIDENTIAL</b><br/>"
        report_classification = Paragraph(classification_text, self.stylesheet["Classification"])
        elements.append(report_classification)

        elements.append(spacer_120)

        title_text = ("<b>DIGITAL RISK<br/>"
                      "ASSESSMENT<br/>"
                      "REPORT</b><br/>"
                      )
        report_title = Paragraph(title_text, self.stylesheet["Title"])
        elements.append(report_title)

        elements.append(spacer_30)

        company_date_text = (f"<b>PREPARED FOR: {company.upper()} <br/>"
                             f"PREPARED ON: {doc_date} </b><br/>")
        company_date = Paragraph(company_date_text, self.stylesheet["h3"])
        elements.append(company_date)

        elements.append(spacer_30)

        person_to_contact_text = (f"<b>PREPARED BY: <br/> {prepared_by} </b><br/>"
                                  f"<b>Email: </b><i> {email} </i><br/>"
                                  f"<b>Mobile: </b><i> {mobile} </i><br/>")
        person_to_contact = Paragraph(person_to_contact_text, self.stylesheet["h3"])
        elements.append(person_to_contact)

        elements.append(PageBreak())

        return elements

    def get_exec_summary(self):
        """
        Returns a list of elements that will form the executive summary section of the PDF.
        """
        logging.info("Creating Executive Summary....")
        elements = []

        # Variables 
        company = self.data["company"]
        doc_date = self.data["doc_date"]
        exposure_amt = '{:,.2f}'.format(
            self.data["exposure_amt"])  # Convert to 2 decimal place in this format 20,000.00
        high_risk_num = self.data["risk_counts"]["high"]
        open_vulnerabilities_num = self.data["vulns"]["count"]

        line_spacer = Spacer(10, 5)

        header_text = '<b>EXECUTIVE SUMMARY</b>'
        header = Paragraph(header_text, self.stylesheet["section"])
        elements.append(header)

        elements.append(line_spacer)

        text = (f"This is an initial risk assessment of {company} conducted on {doc_date} using Protos Labs’ "
                f"proprietary Cyber Risk Intelligence technologies. Overall digital risk exposure and current "
                f"cyber security posture of your organization was evaluated using data on the Open and Dark web "
                f"and reviewed against the current cyber threat landscape."
                )
        exec_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exec_content)

        elements.append(line_spacer)

        text = (f"The overall digital risk exposure of {company} is estimated to be ${exposure_amt}. Leaked "
                f"credentials and {open_vulnerabilities_num} security vulnerabilities were also discovered from "
                f"Open and Dark web scans, of which {high_risk_num} are high-risk findings that must be "
                f"addressed urgently."
                )
        exec_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exec_content)

        elements.append(line_spacer)

        text = ("Cybercrime cases accounted for 43% of Singapore’s overall crime in 2020<super>1</super>, with "
                "an increase of 154% of ransomware cases reported to the Cyber Security Agency of Singapore "
                "(CSA) in the same year. Majority of these affected companies are small and medium enterprises "
                "(SMEs) across sectors including retail and healthcare<super>1</super>. With the cost of a "
                "ransomware attack averaging around S$1.5 million<super>2</super>, the impact can prove more "
                "costly than expected for SMEs like yourself."
                )
        exec_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exec_content)

        elements.append(line_spacer)

        text = ("As we move towards a new post-covid normal and adopt hybrid working arrangements, it is "
                "imperative for companies to adopt cybersecurity solutions to mitigate the risks of "
                "cyber-attacks. Continual assessments of threats and vulnerabilities not only help safeguard "
                "your assets, operation and staff but will also improve your competitiveness relative to "
                "industry peers."
                )
        exec_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exec_content)

        elements.append(line_spacer)

        text = (f"This Digital Risk Assessment (DRA) report provides crucial information which enables {company} "
                f"to: <br/>"
                )
        exec_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exec_content)

        numbered_list = ListFlowable(
            [
                ListItem(Paragraph("Estimate the financial impact of cyber threats", self.stylesheet["normal"])),
                ListItem(Paragraph("Identify and remediate security gaps", self.stylesheet["normal"])),
                ListItem(
                    Paragraph("Make data-driven decisions on cybersecurity investments", self.stylesheet["normal"])),
            ],
            bulletType='1',
            bulletFormat="%s.",
        )

        elements.append(numbered_list)

        return elements

    def get_assessment_scope(self):
        """
        Returns a list of elements that will form the scope of assessment section of the PDF.
        """
        logging.info("Creating scope of assessment....")
        elements = [PageBreak()]

        line_spacer = Spacer(10, 5)
        section_spacer = Spacer(10, 15)

        text = '<b>SCOPE OF ASSESSMENT</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = ("The risk assessment was conducted on your organization’s public-facing digital assets across "
                "six (6) key areas:<br/>")
        assessment_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(assessment_content)

        numbered_list = ListFlowable(
            [
                ListItem(Paragraph("Email Security,", self.stylesheet["normal"])),
                ListItem(Paragraph("Vulnerabilities,", self.stylesheet["normal"])),
                ListItem(Paragraph("Website Configuration,", self.stylesheet["normal"])),
                ListItem(Paragraph("Exposed Services,", self.stylesheet["normal"])),
                ListItem(Paragraph("Leaked Credentials, and", self.stylesheet["normal"])),
                ListItem(Paragraph("Marketplace Mentions.", self.stylesheet["normal"])),
            ],
            bulletType='1',
            bulletFormat="%s.",
        )

        elements.append(numbered_list)

        elements.append(line_spacer)

        text = ("Results of the scans were ingested by Protos Labs’ proprietary risk quantification models to "
                "assess the financial impact of the risks to your organization. Descriptions of each area can "
                "be found in the Appendix.")
        assessment_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(assessment_content)

        elements.append(section_spacer)

        return elements

    def get_methodology(self):
        """
        Returns a list of elements that will form the methodology section of the PDF.
        """
        logging.info("Creating methodology....")
        elements = []

        line_spacer = Spacer(10, 5)

        text = '<b>METHODOLOGY</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = ("Protos Labs’ methodology has been endorsed by the Cybersecurity "
                "Agency of Singapore (CSA) Innovation Committee.")
        methodology_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(methodology_content)

        elements.append(line_spacer)

        text = ("Protos Labs leverages on advanced scanning and collection techniques, "
                "similar to those used by malicious actors, to assess your organization’s "
                "cybersecurity posture from the Open and Dark Web. We also leverage on "
                "specialised tools similar to those used by law enforcement and the military "
                "to gather intelligence on threats that pose as cyber risks to your organization. "
                "These techniques rely solely on information found in the public domain and do not "
                "access any of your organization’s private resources or assets.")
        methodology_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(methodology_content)

        elements.append(line_spacer)

        text = ("We combine the scan results with real-world historical breach data and advanced "
                "Machine Learning algorithms in our Cyber Risk Quantification (CRQ) model to "
                "translate the overall cyber risk exposure of your organization into monetary terms.")
        methodology_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(methodology_content)

        return elements

    def get_digital_risk_exposure(self):
        """
        Returns a list of elements that will form the digital risk exposure section of the PDF.
        """
        logging.info("Creating digital risk exposure page....")
        elements = [PageBreak()]

        # Variables
        exposure_amt = '{:,.2f}'.format(
            self.data["exposure_amt"])  # Convert to 2 decimal place in this format 20,000.00
        threat_categories_risk = self.data["threat_category"]

        line_spacer = Spacer(10, 5)
        graph_spacer = Spacer(10, 30)

        text = '<b>DIGITAL RISK EXPOSURE</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = (
            f"The overall digital risk exposure of your organization is estimated to be <b><u>${exposure_amt}</u></b>.")
        exposure_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exposure_content)

        elements.append(line_spacer)

        text = ("This was derived from estimating the financial costs of the <b>top five (5) cyber threats</b> that "
                "are relevant to your organization and industry (refer to diagram below). The estimates were computed "
                "based on data from peer companies, your organization’s cyber posture and past cyber incidents.")
        exposure_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exposure_content)

        elements.append(graph_spacer)

        text = "<b>Cyber Risk Exposure Breakdown</b><br/>"
        exposure_content = Paragraph(text, self.stylesheet["classification"])
        elements.append(exposure_content)

        # Initialise a Drawing for the graph
        drawing = Drawing(400, 200)
        threat_categories = [threat_category["threatCategory"] for threat_category in threat_categories_risk]
        risks_list = [threat_category["risk"] for threat_category in threat_categories_risk]

        # Convert list to a tuple ([],), which is the accepted data format for the HorizontalBarChart()
        risks = (risks_list,)

        chart = HorizontalBarChart()
        chart.data = risks
        chart.x = 120  # Placement of chart on the document x-axis
        chart.y = -13  # Placement of chart on the document y-axis
        chart.width = 300
        chart.height = 200
        chart.valueAxis.visible = 0  # Hide the chart's x-axis text
        chart.valueAxis.forceZero = 1
        chart.categoryAxis.categoryNames = threat_categories  # Labels on the chart's y-axis
        chart.categoryAxis.strokeColor = self.colors["barChartStrokeColor"]  # Color of the chart's y-axis line
        chart.categoryAxis.labels.fontName = 'Helvetica'  # Font of the chart's y-axis labels
        chart.categoryAxis.labels.fontSize = 9  # Font size of the chart's y-axis labels        
        chart.bars[0].fillColor = self.colors["barChartBarColor"]  # Color of the bars in the chart
        chart.bars.strokeColor = None  # Remove stroke on the bars of the chart
        chart.barWidth = 5  # Thickness of each bar in the chart
        chart.barLabelFormat = '$' + '%d'  # Print out the values next to the bars
        chart.barLabels.nudge = 25  # Formatting to flush the values
        chart.barLabels.fontName = "Helvetica"  # Font of the values next to the bars
        chart.barLabels.fontSize = 9  # Font size of the values next to the bars

        drawing.add(chart)
        elements.append(drawing)

        elements.append(graph_spacer)

        text = (
            "Cyber risk exposures measure the likelihood of cybersecurity attacks occurring and negatively impacting "
            "your business’s information systems, leading to the loss of confidentiality, integrity and availability of data. "
            "The estimated figure of your overall risk exposure indicates potential economic loss in situations where cyber "
            "threats like ransomware attacks, data breaches or business email compromises do occur to your organization.")
        exposure_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(exposure_content)

        return elements

    def get_security_weaknesses(self):
        """
        Returns a list of elements that will form the security weakness section of the PDF.
        """
        logging.info("Creating security weaknesses....")
        elements = [PageBreak()]

        # Variables
        low_risk_num = self.data["risk_counts"]["low"]
        medium_risk_num = self.data["risk_counts"]["medium"]
        high_risk_num = self.data["risk_counts"]["high"]
        leaked_creds_num = self.data["leaked_creds"]["count"]
        open_vulnerabilities_num = self.data["vulns"]["count"]
        email_security_misconfig_num = self.data["email_misconfig_count"]
        creds_dict = self.data["leaked_creds"]["latest"]
        insecure_headers_num = self.data["insecure_headers_count"]
        marketplace_num = self.data["marketplace_mentions"]["total_count"]
        mm_dict = self.data["marketplace_mentions"]["data"]
        exposed_service_num = self.data["exposed_service_count"]

        line_spacer = Spacer(10, 5)

        text = '<b>SECURITY WEAKNESSES</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        # Check which risk level(s) is/are present
        if high_risk_num > 0 and medium_risk_num > 0 and low_risk_num > 0:
            risk_text = (
                f"Protos Labs has discovered a total of <b><u>{high_risk_num} High Risk, {medium_risk_num} Medium Risk and {low_risk_num} Low Risk </u></b> finding(s) based on our open "
                "and dark web scans. These weaknesses include:")
        elif high_risk_num > 0 and medium_risk_num > 0 and low_risk_num == 0:
            risk_text = (
                f"Protos Labs has discovered a total of <b><u>{high_risk_num} High Risk and {medium_risk_num} Medium Risk </u></b> finding(s) based on our open "
                "and dark web scans. These weaknesses include:")
        elif high_risk_num > 0 and medium_risk_num == 0 and low_risk_num > 0:
            risk_text = (
                f"Protos Labs has discovered a total of <b><u>{high_risk_num} High Risk and {low_risk_num} Low Risk </u></b> finding(s) based on our open "
                "and dark web scans. These weaknesses include:")
        elif high_risk_num == 0 and medium_risk_num > 0 and low_risk_num > 0:
            risk_text = (
                f"Protos Labs has discovered a total of <b><u>{medium_risk_num} Medium Risk and {low_risk_num} Low Risk </u></b> finding(s) based on our open "
                "and dark web scans. These weaknesses include:")
        elif high_risk_num > 0 and medium_risk_num == 0 and low_risk_num == 0:
            risk_text = (
                f"Protos Labs has discovered a total of <b><u>{high_risk_num} High Risk </u></b> finding(s) based on our open "
                "and dark web scans. These weaknesses include:")
        elif high_risk_num == 0 and medium_risk_num > 0 and low_risk_num == 0:
            risk_text = (
                f"Protos Labs has discovered a total of <b><u>{medium_risk_num} Medium Risk </u></b> finding(s) based on our open "
                "and dark web scans. These weaknesses include:")
        elif high_risk_num == 0 and medium_risk_num == 0 and low_risk_num > 0:
            risk_text = (
                f"Protos Labs has discovered a total of <b><u>{low_risk_num} Low Risk </u></b> finding(s) based on our open "
                "and dark web scans. These weaknesses include:")

        security_content = Paragraph(risk_text, self.stylesheet["normal"])
        elements.append(security_content)

        # Run if leaked creds is more than 0
        if leaked_creds_num > 0:
            list_text = (
                f"<b>{leaked_creds_num} Leaked Credentials</b> on the dark web (most recent five displayed below). This could "
                "signify hackers have compromised your corporate email accounts. Hackers can buy these credentials "
                "for further access to any sensitive data stored in these accounts. The full list of credentials "
                "can be found in the Appendix.")

            bullet_list = ListFlowable(
                [
                    ListItem(Paragraph(list_text, self.stylesheet["normal"])),
                ],
                bulletType='bullet',
                start='•',
            )

            elements.append(bullet_list)
            elements.append(line_spacer)
            """
            Create table
            """
            table_data = []  # Will be a 2D list with each sublist corresponding to 1 row in the table.

            # Create table headers

            cols = OrderedDict([("<b>No.</b>", ParagraphStyle(name="01",
                                                              parent=self.stylesheet["table-text"],
                                                              alignment=TA_LEFT
                                                              )),
                                ("<b>Email</b>", ParagraphStyle(name="02",
                                                                parent=self.stylesheet["table-text"],
                                                                alignment=TA_LEFT
                                                                )),
                                ("<b>Hash/Password</b>", ParagraphStyle(name="03",
                                                                        parent=self.stylesheet["table-text"],
                                                                        alignment=TA_LEFT
                                                                        )),
                                ("<b>Date of Leak</b>", ParagraphStyle(name="04",
                                                                       parent=self.stylesheet["table-text"],
                                                                       alignment=TA_LEFT
                                                                       )),
                                ("<b>Source</b>", ParagraphStyle(name="05",
                                                                 parent=self.stylesheet["table-text"],
                                                                 alignment=TA_LEFT
                                                                 )),
                                ])
            table_headers = [Paragraph(table_header, self.stylesheet["table-header"]) for table_header in cols.keys()]
            table_data.append(table_headers)

            # Add table data
            for count, data in enumerate(creds_dict):
                line_data = [str(count + 1), data.get('email'), data.get('hash'), data.get('date'), data.get('source')]

                formatted_line_data = [Paragraph(item, item_style) for item, item_style in
                                       zip(line_data, cols.values())]

                table_data.append(formatted_line_data)

            # Create table flowable
            table = Table(table_data, colWidths=[40, 140, 106, 75, 120])
            table.setStyle(self.table_styles["normal"])
            elements.append(table)
            elements.append(line_spacer)

            # Run if marketplace mentions is more than 0
        if marketplace_num > 0:
            list_text = (
                f"<b>{marketplace_num} Marketplace Mentions.</b> Marketplace mentions could signify an interest by hackers to target your organization. Typically, "
                "these are early signs of a compromise and your organization will need to remediate the other findings in the report in order to close any gaps that hackers "
                "can use against you.")

            bullet_list = ListFlowable(
                [
                    ListItem(Paragraph(list_text, self.stylesheet["normal"])),
                ],
                bulletType='bullet',
                start='•',
            )

            elements.append(bullet_list)
            elements.append(line_spacer)

            """
            Create table
            """
            table_data = []  # Will be a 2D list with each sublist corresponding to 1 row in the table.

            # Create table headers

            cols = OrderedDict([("<b>No.</b>", ParagraphStyle(name="01",
                                                              parent=self.stylesheet["table-text"],
                                                              alignment=TA_LEFT
                                                              )),
                                ("<b>Marketplace Name</b>", ParagraphStyle(name="02",
                                                                           parent=self.stylesheet["table-text"],
                                                                           alignment=TA_LEFT
                                                                           )),
                                ("<b>Number of Mentions</b>", ParagraphStyle(name="03",
                                                                             parent=self.stylesheet["table-text"],
                                                                             alignment=TA_LEFT
                                                                             )),
                                ])
            table_headers = [Paragraph(table_header, self.stylesheet["table-header"]) for table_header in cols.keys()]
            table_data.append(table_headers)

            # Add table data
            for count, data in enumerate(mm_dict):
                line_data = [str(count + 1), data.get('name'), str(data.get('count'))]

                formatted_line_data = [Paragraph(item, item_style) for item, item_style in
                                       zip(line_data, cols.values())]

                table_data.append(formatted_line_data)

            # Create table flowable
            table = Table(table_data, colWidths=[45, 291, 145])
            table.setStyle(self.table_styles["normal"])
            elements.append(table)
            elements.append(line_spacer)

        # Run if open vulnerabilities is more than 0
        if open_vulnerabilities_num > 0:
            list_text = (
                f"<b>{open_vulnerabilities_num} Open Vulnerabilities.</b> Open vulnerabilities on your public-facing "
                "digital assets could result in hackers exploiting them to gain access to your organization’s network or data.")

            bullet_list = ListFlowable(
                [
                    ListItem(Paragraph(list_text, self.stylesheet["normal"])),
                ],
                bulletType='bullet',
                start='•',
            )

            elements.append(bullet_list)
            elements.append(line_spacer)

        # Run if email security misconfigurations is more than 0
        if email_security_misconfig_num > 0:
            email_text = (
                f"<b> {email_security_misconfig_num} Email Security Misconfigurations.</b> Weak email security could result in hackers spoofing your email to "
                "disguise as you. Such emails could be sent to your customers or partners to initiate fraudulent activities.")

            bullet_list = ListFlowable(
                [
                    ListItem(Paragraph(email_text, self.stylesheet["normal"])),
                ],
                bulletType='bullet',
                start='•',
            )

            elements.append(bullet_list)
            elements.append(line_spacer)

        # Run if insecure headers is more than 0
        if insecure_headers_num > 0:
            email_text = (
                f"<b> {insecure_headers_num} Insecure Headers.</b> Insecure headers could result in your website being used as a stepping stone to attack your "
                "website’s visitors.")

            bullet_list = ListFlowable(
                [
                    ListItem(Paragraph(email_text, self.stylesheet["normal"])),
                ],
                bulletType='bullet',
                start='•',
            )

            elements.append(bullet_list)
            elements.append(line_spacer)

        # Run if exposed services is more than 0
        if exposed_service_num > 0:
            email_text = (
                f"<b> {exposed_service_num} Exposed Services.</b> Exposed services could result in them being exploited by hackers to gain access to your "
                "organization’s network or data.")

            bullet_list = ListFlowable(
                [
                    ListItem(Paragraph(email_text, self.stylesheet["normal"])),
                ],
                bulletType='bullet',
                start='•',
            )

            elements.append(bullet_list)
            elements.append(line_spacer)

        text = (
            f"<i>High risks describe issues that could be immediately used by bad actors to conduct attacks on your organization. Medium risks describe issues that your "
            "organization should keep track of and make the decision to close or not.  Low risks mean that Protos Labs has found no current issues.</i>")
        security_note = Paragraph(text, self.stylesheet["note"])
        elements.append(security_note)

        return elements

    def get_comparison(self):
        """
        Returns a list of elements that will form the comparison with companies in A/P section of the PDF.
        """
        logging.info("Creating comparison....")
        elements = [PageBreak()]

        # Variables
        company = self.data["company"]
        leaked_creds_percentile = self.data["leaked_creds"]["percentile"]
        open_vulnerabilities_percentile = self.data["vulns"]["percentile"]
        leaked_creds_median = self.data["leaked_creds"]["median"]
        vulns_median = self.data["vulns"]["median"]

        line_spacer = Spacer(10, 5)

        text = '<b>HOW DO YOU COMPARE TO SIMILAR COMPANIES IN ASIA PACIFIC?</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = (
            f"<b>{company}</b> is at the <b>{leaked_creds_percentile}</b> percentile based on the number of leaked credentials exposed compared to similar companies in the Asia Pacific. "
            f"The median number of leaked credentials exposed is <b>{leaked_creds_median}</b>.")
        comparison_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(comparison_content)

        elements.append(line_spacer)

        text = (
            f"<b>{company}</b> is at the <b>{open_vulnerabilities_percentile}</b> percentile based on the number of open vulnerabilities exposed compared to similar companies in the Asia Pacific. The median number of "
            f"open vulnerabilities exposed is <b>{vulns_median}</b>.")
        comparison_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(comparison_content)

        return elements

    def get_findings_and_recommendations(self):
        """
        Returns a list of elements that will form the findings and recommendations section of the PDF.
        """
        logging.info("Creating findings and recommendations page....")
        elements = [PageBreak()]

        # Variables
        findings_dict = self.data["findings"]

        line_spacer = Spacer(10, 5)
        section_spacer = Spacer(10, 15)
        table_spacer = Spacer(10, 25)

        text = '<b>FINDINGS AND RECOMMENDATIONS</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = (
            "The findings of this report are categorized into three risk levels - High, Medium, and Low. This information enables you to effectively prioritize allocation of cybersecurity resources while staying aligned "
            "with your business objectives.")
        findings_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(findings_content)

        elements.append(section_spacer)

        risk_text = {
            "high": {"header": "HIGH RISK FINDINGS",
                     "elab": ("<u>High Risk Findings</u> describe areas of weaknesses that can lead to potential "
                              "significant damage or disruption if they are abused by bad actors. It is recommended "
                              "that these issues be addressed immediately."
                              ),
                     "findings": [finding for finding in findings_dict if finding["level"] == "High Risk"]},
            "medium": {"header": "MEDIUM RISK FINDINGS",
                       "elab": ("<u>Medium Risk Findings</u> describe areas of weaknesses with general risk for "
                                "malicious cyber activities that your organization should take note of."
                                ),
                       "findings": [finding for finding in findings_dict if finding["level"] == "Medium Risk"]},
            "low": {"header": "LOW RISK FINDINGS",
                    "elab": "<u>Low Risk Findings</u> indicate that no abnormal issues were found.",
                    "findings": [finding for finding in findings_dict if finding["level"] == "Low Risk"]}
        }

        for risk_content in risk_text.values():
            findings_content = Paragraph(risk_content["header"], self.stylesheet["h3"])
            elements.append(findings_content)

            elements.append(line_spacer)

            bullet_list = ListFlowable(
                [
                    ListItem(Paragraph(risk_content["elab"], self.stylesheet["normal"])),
                ],
                bulletType='bullet',
                start='•',
            )

            elements.append(bullet_list)

            elements.append(line_spacer)

            """
            Create table
            """
            for idx, data in enumerate(risk_content["findings"]):
                table_data = []  # Will be a 2D list with each sublist corresponding to 1 row in the table.

                # Create table headers
                cols = OrderedDict([("<b>No</b>.", ParagraphStyle(name="01",
                                                                  parent=self.stylesheet["table-text"],
                                                                  alignment=TA_LEFT
                                                                  )),
                                    ("<b>Area</b>", ParagraphStyle(name="02",
                                                                   parent=self.stylesheet["table-text"],
                                                                   alignment=TA_LEFT
                                                                   )),
                                    ("<b>Finding</b>", ParagraphStyle(name="03",
                                                                      parent=self.stylesheet["table-text"],
                                                                      alignment=TA_LEFT
                                                                      )),
                                    ("<b>Potential Impact</b>", ParagraphStyle(name="04",
                                                                               parent=self.stylesheet["table-text"],
                                                                               alignment=TA_LEFT
                                                                               )),
                                    ])
                table_headers = [Paragraph(table_header, self.stylesheet["table-header"]) for table_header in
                                 cols.keys()]

                # Add table data
                table_data.append(table_headers)

                line_data = [str(idx + 1), data.get('area'), data.get('finding'), data.get('impact')]

                formatted_line_data = [Paragraph(item, item_style) for item, item_style in
                                       zip(line_data, cols.values())]

                table_data.append(formatted_line_data)

                # Create table flowable
                table = Table(table_data, colWidths=[38, 93, 200, 150])
                table.setStyle(self.table_styles["normal"])
                elements.append(table)

                elements.append(line_spacer)

                rec_text = (data.get("rec"))
                if rec_text:
                    text = "<b>Recommendations</b><br/>"
                    recommendation_header = Paragraph(text, self.stylesheet["normal"])
                    elements.append(recommendation_header)
                    risks = Paragraph(rec_text, self.stylesheet["normal"])
                    elements.append(risks)
                    elements.append(PageBreak())

        return elements

    def get_landscape(self):
        """
        Returns a list of elements that will form the threat landscape section of the PDF.
        """
        logging.info("Creating threat landscape....")
        elements = [PageBreak()]

        line_spacer = Spacer(10, 5)

        text = '<b>OVERVIEW OF CYBER THREAT LANDSCAPE</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        for para in industry2landscape.get(applnindustry2rptindustry.get(self.industry, "general"), "general"):
            landscape_content = Paragraph(para, self.stylesheet["normal"])
            elements.append(landscape_content)

            elements.append(line_spacer)

        return elements

    def get_infographic(self):
        """
        Returns a list of elements that will form the infographic section of the PDF.
        """
        logging.info("Creating infographic....")
        elements = [PageBreak()]

        img = Image(industry2info.get(applnindustry2rptindustry.get(self.industry, "general"), "general"),
                    width=6.5 * inch,
                    height=16 * inch,
                    kind='proportional'
                    )
        elements.append(img)

        return elements

    def get_help(self):
        """
        Returns a list of elements that will form the how protos can help section of the PDF.
        """
        logging.info("Creating how protos can help....")
        elements = [PageBreak()]

        line_spacer = Spacer(10, 5)

        text = '<b>HOW CAN WE HELP?</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        text = (
            f"Protos Labs is a Singapore Cyber Risk Intelligence startup founded by ex-Booz Allen cybersecurity consultants. We are innovation partners "
            "of the <b>Cybersecurity Agency of Singapore (CSA)</b> and technology partners to global banks and insurance companies.")
        help_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(help_content)

        elements.append(line_spacer)

        text = (
            "We wear the hat of a cyber attacker to proactively monitor and gather cyber risk intelligence surrounding your company’s digital footprint. "
            "Protos Labs helps you to eliminate the need to hire your own cyber threat intelligence team, lower costs spent on expensive cybersecurity tools "
            "and eliminate the need for time-consuming manual work needed for dark web investigation and reconnaissance. We will proactively and continuously monitor more than 200 dark web and open web data sources and illicit networks for you - "
            "so that you can be prepared and ready for any form of malicious attack.")
        help_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(help_content)

        elements.append(line_spacer)

        text = "Our Services Includes:<br/>"
        help_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(help_content)

        list = ListFlowable(
            [
                ListItem(Paragraph("Cyber Risk Intelligence Monitoring", self.stylesheet["normal"])),
                ListItem(Paragraph("Cyber Risk Quantification", self.stylesheet["normal"])),
                ListItem(Paragraph("Cyber Awareness Training", self.stylesheet["normal"])),
                ListItem(Paragraph("Simulated Phishing Tests", self.stylesheet["normal"])),
                ListItem(Paragraph("Cyber Insurance", self.stylesheet["normal"])),
                ListItem(Paragraph("Incident Response and Forensic Investigation", self.stylesheet["normal"])),
                ListItem(Paragraph("Post-Incident Remediation Support", self.stylesheet["normal"])),
                ListItem(
                    Paragraph("Third-party Vendor Management and Recommendation Service", self.stylesheet["normal"])),
                ListItem(Paragraph("Cyber Risk Management Advisory", self.stylesheet["normal"])),
            ],
            bulletType='bullet',
            start='•',
        )

        elements.append(list)

        elements.append(line_spacer)

        text = (f"For more information regarding our services, please kindly contact Gilbert Choo, our Lead of Cyber "
                "Engagement at gilbert_choo@protoslabs.sg.<br/>")
        landscape_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(landscape_content)

        return elements

    def get_packages(self):
        """
        Returns a list of elements that will form the packages section of the PDF.
        """
        logging.info("Creating packages....")
        elements = [NextPageTemplate('landscape'), PageBreak()]

        line_spacer = Spacer(10, 5)

        text = '<b>OUR SERVICE PACKAGES</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        img = Image("src/lib/asset/services/packages.jpg",
                    width=16 * inch,
                    height=6.3 * inch,
                    kind='proportional'
                    )
        elements.append(img)

        elements.append(line_spacer)

        elements.append(NextPageTemplate('portrait'))

        return elements

    def get_services(self):
        """
        Returns a list of elements that will form the services section of the PDF.
        """
        logging.info("Creating services....")
        elements = [PageBreak()]

        line_spacer = Spacer(10, 5)
        section_spacer = Spacer(10, 15)

        text = '<b>OUR SERVICES</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = 'PROACTIVE SERVICES'
        paragraph_report_header = Paragraph(text, self.stylesheet["h3"])
        elements.append(paragraph_report_header)

        img = Image("src/lib/asset/services/offerings_proactive_1.jpg",
                    width=6.7 * inch,
                    height=16 * inch,
                    kind='proportional'
                    )
        elements.append(img)

        elements.append(PageBreak())

        img = Image("src/lib/asset/services/offerings_proactive_2.jpg",
                    width=6.7 * inch,
                    height=16 * inch,
                    kind='proportional'
                    )
        elements.append(img)

        elements.append(section_spacer)

        text = 'REACTIVE SERVICES'
        paragraph_report_header = Paragraph(text, self.stylesheet["h3"])
        elements.append(paragraph_report_header)

        img = Image("src/lib/asset/services/offerings_reactive.jpg",
                    width=6.7 * inch,
                    height=16 * inch,
                    kind='proportional'
                    )
        elements.append(img)

        return elements

    def get_faq(self):
        """
        Returns a list of elements that will form the faq section of the PDF.
        """
        logging.info("Creating faq....")
        elements = [PageBreak()]

        line_spacer = Spacer(10, 5)

        text = '<b>FREQUENTLY ASKED QUESTIONS (FAQ)</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = ("<b>1. What is the Cyber Risk Exposure and how is it calculated?</b><br/>"
                "Cyber Risk Exposure refers to the annualized financial loss that your organization might experience due "
                "to cyberattacks. This estimate includes direct and indirect losses such as regulatory fines, incident "
                "response cost, legal fees, loss of funds, public relations fees and business and service disruptions. "
                "Protos Labs uses insurance grade risk quantification models that assesses your organization’s defences, "
                "current attacker activity, and historical breaches. For each estimation, we conduct millions of simulations to "
                "predict expected losses that are tailored to your assets and business.")
        paragraph_report_header = Paragraph(text, self.stylesheet["normal"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = ("<b>2. What is the impact of a leaked credential?</b><br/>"
                "Leaked credentials refer to email addresses and passwords that are actively sold by cybercriminals on the dark web. "
                "These are often leaked through third party services that employees sign up using their corporate email addresses. "
                "Leaked credentials can be used by malicious actors to gain initial access to corporate emails or corporate networks, "
                "especially if the leaked credentials match those used by employees in their corporate accounts. This could then lead to "
                "more sophisticated attacks such as ransomware or impersonation of executives for fraudulent transfers.")
        paragraph_report_header = Paragraph(text, self.stylesheet["normal"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = ("<b>3. My credentials appeared in the report; however, the password is incorrect.</b><br/>"
                "When your credentials are leaked on the dark web, it could come from multiple data sources new and old. These data sources "
                "include data breaches on third-party platforms that you have signed up an account using your work email address. The "
                "platform name will be provided if such data are available. There could also be a possibility that your email address is "
                "acquired but the malicious actor added in a fake password to sell/resell it on the dark web. Nevertheless, we recommend that "
                "you change your password and secure your email account using a Multi-Factor Authentication (MFA) tool.")
        paragraph_report_header = Paragraph(text, self.stylesheet["normal"])
        elements.append(paragraph_report_header)

        elements.append(PageBreak())

        text = (f"<b>4. How are your scans conducted and will it affect my network?</b><br/>"
                "Protos Labs leverages advanced scanning and collection techniques, similar to those used by malicious actors, to assess your "
                "organization’s cybersecurity posture from the Open and Dark Web. We also leverage specialized tools similar to those used by "
                "law enforcement and the military to gather intelligence on threats that pose as cyber risks to your organization.  These "
                "techniques rely solely on information found in the public domain and do not access any of your organization’s private "
                "resources or assets.")
        paragraph_report_header = Paragraph(text, self.stylesheet["normal"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = (f"<b>5.	I do not understand the technical recommendations of this report. What should I do?</b><br/>"
                "The technical recommendations are best implemented by a specialized IT staff or technician. Protos Labs works with a community of "
                "trusted service provider, if you require any help, please feel free to reach out to us and we will be happy to assist you.<br/><br/>")
        paragraph_report_header = Paragraph(text, self.stylesheet["normal"])
        elements.append(paragraph_report_header)

        return elements

    def get_glossary(self):
        """
        Returns a list of elements that will form the glossary section of the PDF.
        """
        logging.info("Creating glossary....")
        elements = [PageBreak()]

        line_spacer = Spacer(10, 5)

        text = '<b>GLOSSARY</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        text = (
            f"<b>Cyber Risk Exposure:</b> Your annual cyber risk exposure is assessed based on security defences in the public domain, real-world historical data "
            "and expert analysis.")
        glossary_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(glossary_content)

        elements.append(line_spacer)

        text = (
            f"<b>Email Security:</b> Protos Labs has checked your email security to assess whether they are susceptible to phishing attacks and email spam. Emails can be a "
            "common point of entry for attackers looking to conduct phishing attacks on your employees or to plant malicious software (malware) on your computers.")
        glossary_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(glossary_content)

        elements.append(line_spacer)

        text = (
            f"<b>Vulnerabilities:</b> Protos Labs has scanned your public-facing assets to assess for vulnerabilities that threat actors can exploit. Vulnerabilities are weaknesses that, "
            "if exploited, allow threat actors access to your system to install malware or steal sensitive data.")
        glossary_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(glossary_content)

        elements.append(line_spacer)

        text = (
            f"<b>Services:</b> Protos Labs has scanned your public-facing assets to assess for services that can be exploited by threat actors to conduct cyber-attacks.")
        glossary_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(glossary_content)

        elements.append(line_spacer)

        text = (
            f"<b>Leaked Credentials:</b> Protos Labs has scanned the Dark Web for leaked credentials associated to your organization that may be used by threat actors to launch attacks.")
        glossary_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(glossary_content)

        elements.append(line_spacer)

        text = (
            f"<b>Marketplace Mentions:</b> Protos Labs has searched underground cybercriminal forums to check if your data or network access is being sold.")
        glossary_content = Paragraph(text, self.stylesheet["normal"])
        elements.append(glossary_content)

        return elements

    def get_leaked_appendix(self):
        """
        Returns a list of elements that will form the leaked credentials appendix section of the PDF.
        """
        logging.info("Creating leaked credentials appendix....")
        elements = [PageBreak()]

        # Variables
        leaked_creds_num = self.data["leaked_creds"]["count"]

        if leaked_creds_num > 0:
            leaked_creds_list = self.data["leaked_creds"]["data"]

            line_spacer = Spacer(10, 5)
            section_spacer = Spacer(10, 15)

            text = '<b>APPENDIX</b>'
            paragraph_report_header = Paragraph(text, self.stylesheet["section"])
            elements.append(paragraph_report_header)

            elements.append(section_spacer)

            text = '<b>Leaked Credentials</b>'
            paragraph_report_header = Paragraph(text, self.stylesheet["h3"])
            elements.append(paragraph_report_header)

            elements.append(line_spacer)

            """
            Create table
            """
            table_data = []  # Will be a 2D list with each sublist corresponding to 1 row in the table.

            # Create table headers

            cols = OrderedDict([("<b>Email</b>", ParagraphStyle(name="01",
                                                                parent=self.stylesheet["table-text"],
                                                                alignment=TA_LEFT
                                                                )),
                                ("<b>Hash/Password</b>", ParagraphStyle(name="02",
                                                                        parent=self.stylesheet["table-text"],
                                                                        alignment=TA_LEFT
                                                                        )),
                                ("<b>Date</b>", ParagraphStyle(name="03",
                                                               parent=self.stylesheet["table-text"],
                                                               alignment=TA_LEFT
                                                               )),
                                ("<b>Source</b>", ParagraphStyle(name="04",
                                                                 parent=self.stylesheet["table-text"],
                                                                 alignment=TA_LEFT
                                                                 )),
                                ])
            table_headers = [Paragraph(table_header, self.stylesheet["table-header"]) for table_header in cols.keys()]
            table_data.append(table_headers)

            # Add table data
            for count, data in enumerate(leaked_creds_list):
                line_data = [data.get('email'), data.get('hash'), data.get('date'), data.get('source')]

                formatted_line_data = [Paragraph(item, item_style) for item, item_style in
                                       zip(line_data, cols.values())]

                table_data.append(formatted_line_data)

            # Create table flowable
            table = Table(table_data, colWidths=[161, 150, 85, 85])
            table.setStyle(self.table_styles["normal"])
            elements.append(table)

            return elements
        else:
            return []

    def get_vulnerabilities_appendix(self):
        """
        Returns a list of elements that will form the open vulnerabilities appendix section of the PDF.
        """
        logging.info("Creating open vulnerabilities appendix....")
        elements = [PageBreak()]

        # Variables
        open_vulnerabilities_num = self.data["vulns"]["count"]

        if open_vulnerabilities_num > 0:
            open_vulnerabilities_list = self.data["vulns"]["data"]

            line_spacer = Spacer(10, 5)
            section_spacer = Spacer(10, 15)

            text = '<b>APPENDIX</b>'
            paragraph_report_header = Paragraph(text, self.stylesheet["section"])
            elements.append(paragraph_report_header)

            elements.append(section_spacer)

            text = '<b>Open Vulnerabilities</b>'
            paragraph_report_header = Paragraph(text, self.stylesheet["h3"])
            elements.append(paragraph_report_header)

            elements.append(line_spacer)

            """
            Create table
            """
            table_data = []  # Will be a 2D list with each sublist corresponding to 1 row in the table.

            # Create table headers

            cols = OrderedDict([("<b>IP Address</b>", ParagraphStyle(name="01",
                                                                     parent=self.stylesheet["table-text"],
                                                                     alignment=TA_LEFT
                                                                     )),
                                ("<b>CVE</b>", ParagraphStyle(name="02",
                                                              parent=self.stylesheet["table-text"],
                                                              alignment=TA_LEFT
                                                              )),
                                ("<b>CVSS Score</b>", ParagraphStyle(name="03",
                                                                     parent=self.stylesheet["table-text"],
                                                                     alignment=TA_LEFT
                                                                     )),
                                ("<b>Summary</b>", ParagraphStyle(name="04",
                                                                  parent=self.stylesheet["table-text"],
                                                                  alignment=TA_LEFT
                                                                  )),
                                ])
            table_headers = [Paragraph(table_header, self.stylesheet["table-header"]) for table_header in cols.keys()]
            table_data.append(table_headers)

            # Add table data
            for count, data in enumerate(open_vulnerabilities_list):
                line_data = [data.get('ip'), data.get('cve'), str(data.get('cvss')), data.get('summary')]

                formatted_line_data = [Paragraph(item, item_style) for item, item_style in
                                       zip(line_data, cols.values())]

                table_data.append(formatted_line_data)

            # Create table flowable
            table = Table(table_data, colWidths=[75, 75, 55, 276])
            table.setStyle(self.table_styles["normal"])
            elements.append(table)

            return elements
        else:
            return []

    def get_references(self):
        """
        Returns a list of elements that will form the references section of the PDF.
        """
        logging.info("Creating references....")
        elements = [PageBreak()]

        line_spacer = Spacer(10, 5)

        text = '<b>REFERENCES</b>'
        paragraph_report_header = Paragraph(text, self.stylesheet["section"])
        elements.append(paragraph_report_header)

        elements.append(line_spacer)

        for idx, ref in enumerate(industry2ref.get(applnindustry2rptindustry.get(self.industry, "general"), "general")):
            reference_content = Paragraph(f"{idx + 1}.  " + ref, self.stylesheet["normal"])
            elements.append(reference_content)

            elements.append(line_spacer)

        return elements

    def get_elements(self):
        """
        Stitch all elements from each section into one single list of elements that will be rendered.
        """
        sections = (self.get_cover_page(),
                    self.get_exec_summary(),
                    self.get_assessment_scope(),
                    self.get_methodology(),
                    self.get_digital_risk_exposure(),
                    self.get_security_weaknesses(),
                    self.get_comparison(),
                    self.get_findings_and_recommendations(),
                    self.get_landscape(),
                    self.get_infographic(),
                    self.get_help(),
                    self.get_services(),
                    self.get_faq(),
                    self.get_glossary(),
                    self.get_leaked_appendix(),
                    self.get_vulnerabilities_appendix(),
                    self.get_references(),
                    )
        elements = [element for section in sections for element in section]

        return elements
