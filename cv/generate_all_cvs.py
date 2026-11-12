#!/usr/bin/env python3
"""
master_cv: Unified 4-Target WeasyPrint Generator Engine
Author: Diego Alejandro Escobar Barahona
Engine: WeasyPrint 70.0 (Hybrid CLI / Python runner)

Supports 4 production targets:
- de_en:  Data Engineering (English)
- de_es:  Data Engineering (Spanish)
- pub_en: Scientific Research & Publications (English)
- pub_es: Scientific Research & Publications (Spanish)

Enforces:
- Calibrated 1-page compact CSS budget (Letter: 612x792 pt)
- Verbatim UoPeople education blocks across all targets
- Atomic temporary file writes (os.replace in same directory)
- Hybrid runtime resolution (Windows Scoop CLI shim / Linux native import)
"""

import os
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CSSParameters:
    """Calibrated CSS parameters guaranteeing strict 1-page Letter layout."""
    page_margin: str = "5.4mm 13.0mm 5.4mm 13.0mm"
    body_font_size: str = "9.05pt"
    body_line_height: str = "1.14"
    h1_font_size: str = "20pt"
    h2_font_size: str = "10.8pt"
    h2_margin: str = "4.5px 0 1.5px 0"
    ul_margin: str = "0 0 3.5px 0"
    li_padding_left: str = "12px"
    li_margin_bottom: str = "2px"

    def render_css(self) -> str:
        return f"""
:root {{
  --primary: #0f172a;
  --accent: #1e293b;
  --text: #111827;
  --muted: #4b5563;
  --bg: #ffffff;
}}

@page {{
  size: letter;
  margin: {self.page_margin};
  background: var(--bg);
  @bottom-right {{
    content: none;
  }}
}}

*, *::before, *::after {{
  box-sizing: border-box;
}}

html, body {{
  margin: 0;
  padding: 0;
  background: transparent;
}}

body {{
  font-family: 'Liberation Serif', 'Times New Roman', Times, Georgia, serif;
  font-size: {self.body_font_size};
  line-height: {self.body_line_height};
  color: var(--text);
}}

main.document-flow {{
  width: 100%;
  margin: 0;
  padding: 0;
}}

* {{
  border: none;
  border-radius: 0;
  box-shadow: none;
  background: transparent;
  outline: none;
}}

a {{
  color: var(--text);
  text-decoration: none;
}}

h1 {{
  font-family: 'Liberation Serif', 'Times New Roman', Times, Georgia, serif;
  font-size: {self.h1_font_size};
  font-weight: 400;
  text-align: center;
  line-height: {self.body_line_height};
  margin: 0 0 2px 0;
  color: var(--primary);
  letter-spacing: 0.2px;
}}

.role-headline {{
  text-align: center;
  font-size: 9.8pt;
  font-weight: 700;
  line-height: {self.body_line_height};
  margin: 0 0 2.5px 0;
  color: var(--primary);
}}

.contact-line {{
  text-align: center;
  font-size: {self.body_font_size};
  line-height: {self.body_line_height};
  margin: 0 0 1.5px 0;
  color: var(--text);
}}

.contact-subline {{
  text-align: center;
  font-size: {self.body_font_size};
  line-height: {self.body_line_height};
  margin: 0 0 4.5px 0;
  color: var(--text);
}}

.summary-text {{
  margin: 0 0 4.5px 0;
  text-align: left;
  line-height: {self.body_line_height};
}}

h2 {{
  font-family: 'Liberation Serif', 'Times New Roman', Times, Georgia, serif;
  font-size: {self.h2_font_size};
  font-weight: 700;
  line-height: {self.body_line_height};
  margin: {self.h2_margin};
  color: var(--primary);
  break-after: avoid;
  page-break-after: avoid;
}}

hr.section-rule {{
  border-bottom: 1px solid #111827;
  margin: 0 0 3.5px 0;
}}

table.entry-header {{
  width: 100%;
  border-collapse: collapse;
  margin: 1.5px 0 2px 0;
}}

table.entry-header td {{
  padding: 1px 0;
  font-size: {self.body_font_size};
  line-height: {self.body_line_height};
  border-bottom: none;
  vertical-align: baseline;
}}

table.entry-header td.left {{
  text-align: left;
}}

table.entry-header td.right {{
  text-align: right;
  white-space: nowrap;
  padding-left: 10px;
}}

/* ATS Fix for WeasyPrint 70.0: Eliminates orphaned bullet dots during copy/paste */
ul {{
  list-style: none !important;
  padding-left: 0 !important;
  margin: {self.ul_margin};
}}

li {{
  position: relative;
  padding-left: {self.li_padding_left};
  margin-bottom: {self.li_margin_bottom};
  text-align: left;
  line-height: {self.body_line_height};
}}

li::before {{
  content: "•";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--text);
}}

p.skill-row {{
  margin: 0 0 2px 0;
  text-align: left;
  line-height: {self.body_line_height};
}}

tr, figure, li {{
  break-inside: avoid;
  page-break-inside: avoid;
}}
"""


# =============================================================================
# HTML BODY DEFINITIONS (WITH VERBATIM UOPEOPLE EDUCATION BLOCKS)
# =============================================================================

HTML_BODY_DE_EN = """  <main class="document-flow">
    <h1>Diego Alejandro Escobar Barahona</h1>
    <p class="role-headline">Junior Data Engineer &nbsp;|&nbsp; Cloud Data Engineer &nbsp;|&nbsp; Analytics Engineer</p>
    <p class="contact-line">San Salvador, El Salvador &nbsp;|&nbsp; <a href="mailto:diegoalejandroescobarahona1@gmail.com">diegoalejandroescobarahona1@gmail.com</a> &nbsp;|&nbsp; +503 7549 0118</p>
    <p class="contact-subline"><a href="https://www.linkedin.com/in/diego-escobar-459256394">linkedin.com/in/diego-escobar-459256394</a> &nbsp;|&nbsp; <a href="https://github.com/bapatata688">github.com/bapatata688</a> &nbsp;|&nbsp; <a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url">credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10</a></p>

    <h2>Professional Summary</h2>
    <hr class="section-rule">
    <p class="summary-text"><strong>Junior Data Engineer &amp; Analytics Engineer</strong> with enterprise internship experience at <strong>GBM (IBM &amp; Google Cloud Premier Partner)</strong> and experience designing cloud architecture for a <strong>Medallion Data Lakehouse on Google Cloud Platform (GCP)</strong>. <strong>Google Cloud Certified &mdash; Associate Data Practitioner</strong>, fluent in <strong>English (C1 Advanced, EF SET 66/100)</strong>, with hands-on experience in <strong>BigQuery, Dataform (SQLX), SQL, Python, and Spec-Driven Development (SDD)</strong>, and working knowledge of <strong>Datastream CDC, IBM InfoSphere DataStage, and IBM DB2 LUW</strong>.</p>

    <h2>Experience</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>Data Engineer Intern (Digital Solutions Specialist), GBM</strong> &ndash; San Salvador</td>
        <td class="right">July 2026 &ndash; Oct 2026</td>
      </tr>
    </table>
    <ul>
      <li>Designed a <strong>client ETL architecture proposal</strong> for near-real-time cloud replication on <strong>Google Cloud</strong> (<strong>BigQuery, Dataform, Datastream CDC, Cloud Storage</strong>), backed by <strong>Lucidchart</strong> dimensional models and <strong>SQL DDL</strong> scripts.</li>
      <li>Developed and executed <strong>ETL integration jobs under technical mentorship</strong> in <strong>IBM InfoSphere DataStage</strong> (Transformers, Lookups, Joins, Merge) across enterprise test datasets and queried <strong>IBM DB2 LUW</strong> on <strong>Linux RHEL</strong>.</li>
      <li>Supported <strong>auditable cloud governance and FinOps budget estimation</strong> across client proposals by co-authoring <strong>GCP security guidelines</strong> (least-privilege <strong>IAM, MFA</strong>, credential rotation, audit logging, data lineage) and sizing cloud infrastructure in <strong>Google Cloud Pricing Calculator</strong>.</li>
      <li><strong>Co-author | OntoTab (GBM):</strong> Executed empirical benchmark experiments under <strong>5&times;3 nested cross-validation</strong> across <strong>30,000 public credit-risk records</strong> (UCI Taiwan), evaluating ontology-enriched text descriptions encoded via <strong>frozen BGE-M3 (1,024 dims)</strong> across Logistic Regression, XGBoost, and MLP; with XGBoost, text-only ontology representations (R5) reached <strong>0.5069 AP</strong> versus <strong>0.5596 AP</strong> for the engineered numeric baseline (R8) and <strong>0.5568 AP</strong> for the hybrid model (R9), motivating a separate structured numeric channel.</li>
    </ul>

    <h2>Projects</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong><a href="https://github.com/bapatata688/Ferrostats">FERROSTATS</a> &mdash; Cloud-Native Medallion Data Lakehouse &amp; Streaming Pipeline on GCP</strong></td>
        <td class="right"><a href="https://github.com/bapatata688/Ferrostats">GitHub</a> &nbsp;|&nbsp; <a href="https://datastudio.google.com/reporting/2389e684-fc9b-431d-9c56-487b3067eb87/page/p_dwbfqrtk8d">Looker Studio BI</a> &nbsp;|&nbsp; <a href="https://ferrostats-bi-platform-s72yk4nsvq-uc.a.run.app">Live App</a></td>
      </tr>
    </table>
    <ul>
      <li>Architected a cloud-native <strong>Medallion Data Lakehouse (Bronze / Silver / Gold)</strong> in <strong>Google BigQuery</strong> orchestrated via <strong>Google Dataform</strong>, structuring <strong>4 core Bronze tables</strong> (<code>raw_sales</code>, <code>raw_sale_items</code>, <code>raw_products</code>, <code>raw_inventory_movements</code>), <strong>3 Silver staging views</strong> (<code>stg_sales</code>, <code>stg_sale_items</code>, <code>stg_products</code>) with automated data quality assertions, and <strong>3 Gold Star Schema analytical marts</strong> (<code>fct_daily_sales</code>, <code>mart_inventory_pareto_abc</code>, <code>dim_products</code>).</li>
      <li>Defined functional specifications under <strong>Spec-Driven Development (SDD)</strong> for 80/20 Pareto ABC inventory segmentation, Daily Burn Rate, Days of Inventory (DOI), and Reorder Point (ROP), directing and validating AI-assisted SQLX implementations to power a <strong>3-page Google Looker Studio executive dashboard</strong>.</li>
      <li>Specified a decoupled ingestion architecture with <strong>asynchronous REST API streaming into BigQuery Bronze</strong>, establishing transactional concurrency rules and UUID idempotency under <strong>Spec-Driven Development (SDD)</strong>.</li>
      <li>Configured a <strong>FinOps architecture (&lt;$1/mo) on GCP</strong> leveraging the Free Tier for portfolio project deployment across <strong>Cloud Run and BigQuery</strong>.</li>
    </ul>

    <h2>Skills</h2>
    <hr class="section-rule">
    <p class="skill-row"><strong>Cloud &amp; Data Warehouses:</strong> Google Cloud Platform (BigQuery, Dataform SQLX, Cloud Storage, Cloud Run, Looker Studio, IAM, FinOps &amp; Pricing Calculator), working knowledge of Datastream CDC</p>
    <p class="skill-row"><strong>Data Modeling &amp; Pipelines:</strong> Medallion Architecture (Bronze/Silver/Gold), Star Schema (Fact/Dimension Tables), Data Quality Assertions, Lucidchart, familiar with IBM InfoSphere DataStage</p>
    <p class="skill-row"><strong>Languages &amp; Methodologies:</strong> SQL (GoogleSQL, CTEs, DDL/DML), Python 3.11 (Pandas, NumPy), Spec-Driven Development (SDD), AI-Assisted Workflows, Bash, PowerShell</p>
    <p class="skill-row"><strong>Databases &amp; Infrastructure:</strong> Familiar with IBM DB2 LUW and Linux RHEL, Docker, Git/SSH, Azure DevOps</p>
    <p class="skill-row"><strong>Spoken Languages:</strong> Spanish (Native), English (C1 Advanced &mdash; EF SET 66/100)</p>

    <h2>Certifications</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url"><strong>Google Cloud Certified &mdash; Associate Data Practitioner</strong> (ID: 23e3584a246f4c149f26fea03cebcbbb)</a></td>
        <td class="right">Oct 2026 &ndash; Oct 2029</td>
      </tr>
      <tr>
        <td class="left"><strong>Google Cloud Skill Badges: Derive Insights from Data &nbsp;|&nbsp; Prepare Data for Looker Dashboards and Reports</strong></td>
        <td class="right">Aug 2026</td>
      </tr>
      <tr>
        <td class="left"><a href="https://cert.efset.org/93nXaa"><strong>EF SET English Certificate &mdash; C1 Advanced (66/100: Listening C2, Reading C1, Speaking C1)</strong></a></td>
        <td class="right">Jan 2026</td>
      </tr>
      <tr>
        <td class="left"><strong>Code in Place (Python Programming) &mdash; Stanford University</strong></td>
        <td class="right">2026</td>
      </tr>
    </table>

    <h2>Education</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>University of the People</strong> &mdash; Pasadena, California, USA</td>
        <td class="right">Admitted | Term 3, 2027</td>
      </tr>
      <tr>
        <td class="left"><strong>Bachelor of Science in Computer Science</strong></td>
        <td class="right">WSCUC-accredited institution | 100% Online</td>
      </tr>
      <tr>
        <td class="left"><strong>Technical Baccalaureate in Software Development</strong> &ndash; Instituto Nacional San Luis &nbsp;|&nbsp; <em>GPA: 9.5/10.0</em></td>
        <td class="right">2026</td>
      </tr>
    </table>
  </main>"""

HTML_BODY_DE_ES = """  <main class="document-flow">
    <h1>Diego Alejandro Escobar Barahona</h1>
    <p class="role-headline">Junior Data Engineer &nbsp;|&nbsp; Cloud Data Engineer &nbsp;|&nbsp; Analytics Engineer</p>
    <p class="contact-line">San Salvador, El Salvador &nbsp;|&nbsp; <a href="mailto:diegoalejandroescobarahona1@gmail.com">diegoalejandroescobarahona1@gmail.com</a> &nbsp;|&nbsp; +503 7549 0118</p>
    <p class="contact-subline"><a href="https://www.linkedin.com/in/diego-escobar-459256394">linkedin.com/in/diego-escobar-459256394</a> &nbsp;|&nbsp; <a href="https://github.com/bapatata688">github.com/bapatata688</a> &nbsp;|&nbsp; <a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url">credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10</a></p>

    <h2>Perfil Profesional</h2>
    <hr class="section-rule">
    <p class="summary-text"><strong>Junior Data Engineer &amp; Analytics Engineer</strong> con experiencia de pasant&iacute;a empresarial en <strong>GBM (IBM &amp; Google Cloud Premier Partner)</strong> y experiencia dise&ntilde;ando arquitectura Cloud para un <strong>Data Lakehouse Medallion en Google Cloud Platform (GCP)</strong>. <strong>Google Cloud Certified &mdash; Associate Data Practitioner</strong>, con <strong>ingl&eacute;s C1 Avanzado (EF SET 66/100)</strong>, experiencia pr&aacute;ctica en <strong>BigQuery, Dataform (SQLX), SQL, Python y Spec-Driven Development (SDD)</strong>, y conocimiento funcional de <strong>Datastream CDC, IBM InfoSphere DataStage e IBM DB2 LUW</strong>.</p>

    <h2>Experiencia</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>Data Engineer Intern (Digital Solutions Specialist), GBM</strong> &ndash; San Salvador</td>
        <td class="right">Julio 2026 &ndash; Oct 2026</td>
      </tr>
    </table>
    <ul>
      <li>Dise&ntilde;&eacute; una <strong>propuesta de arquitectura ETL para cliente</strong> orientada a replicaci&oacute;n casi en tiempo real en <strong>Google Cloud</strong> (<strong>BigQuery, Dataform, Datastream CDC, Cloud Storage</strong>), respaldada por modelos dimensionales en <strong>Lucidchart</strong> y scripts <strong>SQL DDL</strong>.</li>
      <li>Desarroll&eacute; y ejecut&eacute; <strong>jobs de integraci&oacute;n ETL bajo mentor&iacute;a t&eacute;cnica</strong> en <strong>IBM InfoSphere DataStage</strong> (Transformers, Lookups, Joins, Merge) sobre datasets de prueba empresariales y realic&eacute; consultas en <strong>IBM DB2 LUW</strong> sobre <strong>Linux RHEL</strong>.</li>
      <li>Apoy&eacute; la estructuraci&oacute;n de <strong>gobierno de datos auditable y estimaci&oacute;n presupuestaria FinOps</strong> en propuestas cloud al co-redactar <strong>lineamientos de seguridad en GCP</strong> (<strong>IAM</strong> de privilegio m&iacute;nimo, <strong>MFA</strong>, rotaci&oacute;n de credenciales, linaje de datos) y dimensionar infraestructura en <strong>Google Cloud Pricing Calculator</strong>.</li>
      <li><strong>Coautor | OntoTab (GBM):</strong> Ejecut&eacute; experimentos emp&iacute;ricos bajo validaci&oacute;n cruzada anidada (<strong>5&times;3 nested CV</strong>) sobre <strong>30,000 registros p&uacute;blicos de cr&eacute;dito</strong> (UCI Taiwan), evaluando descripciones enriquecidas con ontolog&iacute;as codificadas mediante <strong>BGE-M3 congelado (1,024 dims)</strong> en Regresi&oacute;n Log&iacute;stica, XGBoost y MLP; en XGBoost, el brazo de texto con ontolog&iacute;a (R5) alcanz&oacute; <strong>0.5069 AP</strong> frente a <strong>0.5596 AP</strong> del baseline num&eacute;rico estructurado (R8) y <strong>0.5568 AP</strong> en el modelo h&iacute;brido (R9), demostrando la importancia de preservar canales num&eacute;ricos tipados.</li>
    </ul>

    <h2>Proyectos</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong><a href="https://github.com/bapatata688/Ferrostats">FERROSTATS</a> &mdash; Data Lakehouse Medall&oacute;n Cloud-Native y Pipeline de Ingesta Streaming en GCP</strong></td>
        <td class="right"><a href="https://github.com/bapatata688/Ferrostats">GitHub</a> &nbsp;|&nbsp; <a href="https://datastudio.google.com/reporting/2389e684-fc9b-431d-9c56-487b3067eb87/page/p_dwbfqrtk8d">Looker Studio BI</a> &nbsp;|&nbsp; <a href="https://ferrostats-bi-platform-s72yk4nsvq-uc.a.run.app">App en Vivo</a></td>
      </tr>
    </table>
    <ul>
      <li>Dise&ntilde;&eacute; la arquitectura Cloud de un <strong>Data Lakehouse Medall&oacute;n (Bronze / Silver / Gold)</strong> en <strong>Google BigQuery</strong> orquestado con <strong>Google Dataform</strong>, estructurando <strong>4 tablas principales en Bronze</strong> (<code>raw_sales</code>, <code>raw_sale_items</code>, <code>raw_products</code>, <code>raw_inventory_movements</code>), <strong>3 vistas en Silver</strong> (<code>stg_sales</code>, <code>stg_sale_items</code>, <code>stg_products</code>) con aserciones de calidad y <strong>3 Data Marts Gold en Esquema Estrella</strong> (<code>fct_daily_sales</code>, <code>mart_inventory_pareto_abc</code>, <code>dim_products</code>).</li>
      <li>Defin&iacute; las especificaciones funcionales bajo <strong>Spec-Driven Development (SDD)</strong> para segmentaci&oacute;n Pareto ABC (80/20), Burn Rate, D&iacute;as de Inventario (DOI) y Punto de Reorden (ROP), dirigiendo y validando la implementaci&oacute;n asistida por IA en SQLX para alimentar un <strong>reporte ejecutivo de 3 p&aacute;ginas en Google Looker Studio</strong>.</li>
      <li>Especific&eacute; una arquitectura de ingesta desacoplada con <strong>streaming as&iacute;ncrono v&iacute;a REST API hacia BigQuery Bronze</strong>, estableciendo reglas de concurrencia transaccional e idempotencia por UUID bajo <strong>Spec-Driven Development (SDD)</strong>.</li>
      <li>Configur&eacute; una <strong>arquitectura FinOps (&lt;$1/mes) en GCP</strong> aprovechando la capa gratuita (Free Tier) para el despliegue del proyecto de portafolio en <strong>Cloud Run y BigQuery</strong>.</li>
    </ul>

    <h2>Habilidades</h2>
    <hr class="section-rule">
    <p class="skill-row"><strong>Cloud y Data Warehouses:</strong> Google Cloud Platform (BigQuery, Dataform SQLX, Cloud Storage, Cloud Run, Looker Studio, IAM, FinOps y Pricing Calculator), conocimiento funcional de Datastream CDC</p>
    <p class="skill-row"><strong>Modelado de Datos y Pipelines:</strong> Arquitectura Medallion (Bronze/Silver/Gold), Esquema Estrella (Hechos y Dimensiones), Aserciones de Calidad de Datos, Lucidchart, familiaridad con IBM InfoSphere DataStage</p>
    <p class="skill-row"><strong>Lenguajes y Metodolog&iacute;as:</strong> SQL (GoogleSQL, CTEs, DDL/DML), Python 3.11 (Pandas, NumPy), Spec-Driven Development (SDD), Desarrollo Asistido por IA, Bash, PowerShell</p>
    <p class="skill-row"><strong>Bases de Datos e Infraestructura:</strong> Familiaridad con IBM DB2 LUW y Linux RHEL, Docker, Git/SSH, Azure DevOps</p>
    <p class="skill-row"><strong>Idiomas:</strong> Espa&ntilde;ol (Nativo), Ingl&eacute;s (C1 Avanzado &mdash; EF SET 66/100)</p>

    <h2>Certificaciones</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url"><strong>Google Cloud Certified &mdash; Associate Data Practitioner</strong> (ID: 23e3584a246f4c149f26fea03cebcbbb)</a></td>
        <td class="right">Oct 2026 &ndash; Oct 2029</td>
      </tr>
      <tr>
        <td class="left"><strong>Google Cloud Skill Badges: Derive Insights from Data &nbsp;|&nbsp; Prepare Data for Looker Dashboards and Reports</strong></td>
        <td class="right">Ago 2026</td>
      </tr>
      <tr>
        <td class="left"><a href="https://cert.efset.org/93nXaa"><strong>EF SET English Certificate &mdash; C1 Avanzado (66/100: Listening C2, Reading C1, Speaking C1)</strong></a></td>
        <td class="right">Ene 2026</td>
      </tr>
      <tr>
        <td class="left"><strong>Code in Place (Python Programming) &mdash; Stanford University</strong></td>
        <td class="right">2026</td>
      </tr>
    </table>

    <h2>Educaci&oacute;n</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>University of the People</strong> &mdash; Pasadena, California, USA</td>
        <td class="right">Admitted | Term 3, 2027</td>
      </tr>
      <tr>
        <td class="left"><strong>Bachelor of Science in Computer Science</strong></td>
        <td class="right">WSCUC-accredited institution | 100% Online</td>
      </tr>
      <tr>
        <td class="left"><strong>Bachillerato T&eacute;cnico Vocacional en Desarrollo de Software</strong> &ndash; Instituto Nacional San Luis &nbsp;|&nbsp; <em>Promedio: 9.5/10.0</em></td>
        <td class="right">2026</td>
      </tr>
    </table>
  </main>"""

HTML_BODY_PUB_EN = """  <main class="document-flow">
    <h1>Diego Alejandro Escobar Barahona</h1>
    <p class="role-headline">Junior Data Engineer &nbsp;|&nbsp; Cloud Data Engineer &nbsp;|&nbsp; Analytics Engineer</p>
    <p class="contact-line">San Salvador, El Salvador &nbsp;|&nbsp; <a href="mailto:diegoalejandroescobarahona1@gmail.com">diegoalejandroescobarahona1@gmail.com</a> &nbsp;|&nbsp; +503 7549 0118</p>
    <p class="contact-subline"><a href="https://www.linkedin.com/in/diego-escobar-459256394">linkedin.com/in/diego-escobar-459256394</a> &nbsp;|&nbsp; <a href="https://github.com/bapatata688">github.com/bapatata688</a> &nbsp;|&nbsp; <a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url">credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10</a></p>

    <h2>Professional Summary</h2>
    <hr class="section-rule">
    <p class="summary-text"><strong>Junior Data Engineer &amp; Analytics Engineer</strong> with enterprise internship experience at <strong>GBM (IBM &amp; Google Cloud Premier Partner)</strong> and co-author in empirical credit risk research (OntoTab, 30,000 records). <strong>Google Cloud Certified Associate Data Practitioner</strong> with solid foundation in cloud ELT architectures on <strong>Google Cloud (BigQuery, Dataform SQLX, Datastream CDC)</strong>, integration tasks in <strong>IBM InfoSphere DataStage, IBM DB2 LUW on Linux RHEL</strong>, tabular statistical modeling in <strong>Python (XGBoost, Pandas, PyArrow)</strong>, and <strong>SQL</strong>. Fluent in English (<strong>EF SET C1 Advanced, 66/100, Listening C2 Proficient</strong>).</p>

    <h2>Scientific Research &amp; Publications</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>OntoTab: A Controlled Study of Ontology-Enriched Text for Tabular Credit Risk</strong> &ndash; <em>Co-author (2nd of 7), GBM</em></td>
        <td class="right">2026</td>
      </tr>
    </table>
    <ul>
      <li>Executed baseline experiments (Activity E01) evaluating <strong>30,000 credit records</strong> (UCI Taiwan, 22.12% default rate) across Logistic Regression, XGBoost, and MLP using <strong>5&times;3 stratified nested cross-validation</strong> and <strong>2,000 paired bootstrap iterations</strong> via CLI workflows.</li>
      <li>Analyzed performance metrics <strong>supporting the finding that structured numerical representations outperformed frozen text embeddings in the evaluated experimental setting</strong> (<strong>0.5596 AP with XGBoost</strong> vs 0.5069 AP with R5 text representation).</li>
    </ul>

    <h2>Experience</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>Data Engineer Intern (Digital Solutions Specialist), GBM</strong> &ndash; San Salvador</td>
        <td class="right">July 2026 &ndash; Oct 2026</td>
      </tr>
    </table>
    <ul>
      <li>Designed an <strong>ELT cloud replication architecture proposal</strong> on <strong>Google Cloud</strong> (<strong>BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage</strong>) delivering <strong>Lucidchart</strong> data flow diagrams and <strong>SQL DDL</strong> scripts.</li>
      <li>Developed and executed <strong>hands-on ETL integration tasks under technical mentorship</strong> in <strong>IBM InfoSphere DataStage</strong> (Transformers, Lookups, Joins, Merge, Funnel) across enterprise test datasets, querying <strong>IBM DB2 LUW</strong> on <strong>Linux RHEL</strong>.</li>
      <li>Assisted in formulating GCP cloud governance frameworks and FinOps budget validations (least-privilege <strong>IAM, Service Accounts</strong>, credential rotation) and infrastructure sizing in <strong>Google Cloud Pricing Calculator</strong>.</li>
    </ul>

    <h2>Projects</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong><a href="https://github.com/bapatata688/Ferrostats">FERROSTATS</a> &mdash; Cloud-Native Medallion Data Lakehouse &amp; Streaming Pipeline on GCP</strong></td>
        <td class="right"><a href="https://github.com/bapatata688/Ferrostats">GitHub</a> &nbsp;|&nbsp; <a href="https://datastudio.google.com/reporting/2389e684-fc9b-431d-9c56-487b3067eb87/page/p_dwbfqrtk8d">Looker Studio BI</a> &nbsp;|&nbsp; <a href="https://ferrostats-bi-platform-s72yk4nsvq-uc.a.run.app">Live App</a></td>
      </tr>
    </table>
    <ul>
      <li>Architected a cloud-native <strong>Medallion Lakehouse (Bronze / Silver / Gold)</strong> in <strong>Google BigQuery</strong> with <strong>Dataform SQLX</strong>, structuring 4 core Bronze tables into curated Silver views and <strong>3 Gold Star Schema analytical marts</strong> (<code>fct_daily_sales</code>, <code>mart_inventory_pareto_abc</code>, <code>dim_products</code>).</li>
      <li>Formulated functional specifications under <strong>Spec-Driven Development (SDD)</strong> for 80/20 Pareto ABC inventory segmentation, Daily Burn Rate, and DOI, powering a 3-page executive dashboard in <strong>Looker Studio</strong> with analytical SQL window functions.</li>
      <li>Specified a decoupled ingestion architecture with <strong>asynchronous REST API streaming into BigQuery Bronze</strong>, establishing transactional concurrency rules and UUID idempotency under <strong>Spec-Driven Development (SDD)</strong>, and configured a <strong>FinOps architecture (&lt;$1/mo) on GCP</strong> leveraging the Free Tier across <strong>Cloud Run and BigQuery</strong>.</li>
    </ul>

    <h2>Skills</h2>
    <hr class="section-rule">
    <p class="skill-row"><strong>Cloud &amp; Warehouses:</strong> Google Cloud Platform (BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage, Cloud Run, Looker Studio, IAM Service Accounts, Cloud Logging/Monitoring, FinOps)</p>
    <p class="skill-row"><strong>Machine Learning &amp; Modeling:</strong> 5x3 Nested Cross-Validation, Bootstrap Resampling, XGBoost, Logistic Regression, BGE-M3 Embeddings, Average Precision (AP), Medallion Architecture, Star Schema</p>
    <p class="skill-row"><strong>Languages &amp; Querying:</strong> SQL (GoogleSQL, PostgreSQL 18, Window Functions, CTEs, Anti-joins, DDL/DML), Python 3.11 (Pandas, PyArrow, NumPy), Bash, PowerShell, Docker, Linux RHEL, Git/SSH</p>
    <p class="skill-row"><strong>Languages:</strong> Spanish (Native), English (C1 Advanced &mdash; EF SET 66/100, Listening C2 Proficient)</p>

    <h2>Certifications</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url"><strong>Google Cloud Certified &mdash; Associate Data Practitioner</strong> (Cert ID: 23e3584a246f4c149f26fea03cebcbbb)</a></td>
        <td class="right">Oct 2026 &ndash; Oct 2029</td>
      </tr>
      <tr>
        <td class="left"><strong>Google Cloud Skill Badges: Derive Insights from Data &nbsp;|&nbsp; Prepare Data for Looker Dashboards and Reports</strong></td>
        <td class="right">Aug 2026</td>
      </tr>
      <tr>
        <td class="left"><a href="https://cert.efset.org/93nXaa"><strong>EF SET English Certificate &mdash; C1 Advanced</strong> (66/100 global &bull; Listening 75 C2 &bull; Speaking 69 C1)</a></td>
        <td class="right">Jan 2026</td>
      </tr>
      <tr>
        <td class="left"><strong>Code in Place (Python Programming) &mdash; Stanford University</strong></td>
        <td class="right">2026</td>
      </tr>
    </table>

    <h2>Education</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>University of the People</strong> &mdash; Pasadena, California, USA</td>
        <td class="right">Admitted | Term 3, 2027</td>
      </tr>
      <tr>
        <td class="left"><strong>Bachelor of Science in Computer Science</strong></td>
        <td class="right">WSCUC-accredited institution | 100% Online</td>
      </tr>
      <tr>
        <td class="left"><strong>Technical Baccalaureate in Software Development</strong> &ndash; Instituto Nacional San Luis &nbsp;|&nbsp; <em>GPA: 9.5/10.0</em></td>
        <td class="right">2026</td>
      </tr>
    </table>
  </main>"""

HTML_BODY_PUB_ES = """  <main class="document-flow">
    <h1>Diego Alejandro Escobar Barahona</h1>
    <p class="role-headline">Junior Data Engineer &nbsp;|&nbsp; Cloud Data Engineer &nbsp;|&nbsp; Analytics Engineer</p>
    <p class="contact-line">San Salvador, El Salvador &nbsp;|&nbsp; <a href="mailto:diegoalejandroescobarahona1@gmail.com">diegoalejandroescobarahona1@gmail.com</a> &nbsp;|&nbsp; +503 7549 0118</p>
    <p class="contact-subline"><a href="https://www.linkedin.com/in/diego-escobar-459256394">linkedin.com/in/diego-escobar-459256394</a> &nbsp;|&nbsp; <a href="https://github.com/bapatata688">github.com/bapatata688</a> &nbsp;|&nbsp; <a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url">credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10</a></p>

    <h2>Perfil Profesional</h2>
    <hr class="section-rule">
    <p class="summary-text"><strong>Junior Data Engineer &amp; Analytics Engineer</strong> con experiencia empresarial en <strong>GBM (Premier Partner de IBM y Google Cloud)</strong> y coautor en investigaci&oacute;n cient&iacute;fica en riesgo crediticio (OntoTab, 30,000 registros). <strong>Google Cloud Certified Associate Data Practitioner</strong>, con s&oacute;lidas bases en arquitecturas ELT en <strong>Google Cloud (BigQuery, Dataform SQLX, Datastream CDC)</strong>, tareas de integraci&oacute;n en <strong>IBM InfoSphere DataStage, IBM DB2 LUW sobre Linux RHEL</strong>, modelado estad&iacute;stico tabular en <strong>Python (XGBoost, Pandas, PyArrow)</strong> y <strong>SQL</strong>. Biling&uuml;e con <strong>Ingl&eacute;s C1 Avanzado (EF SET 66/100, Listening C2 Proficient)</strong>.</p>

    <h2>Investigaci&oacute;n Cient&iacute;fica</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>OntoTab: A Controlled Study of Ontology-Enriched Text for Tabular Credit Risk</strong> &ndash; <em>Coautor (2.&ordm; de 7), GBM</em></td>
        <td class="right">2026</td>
      </tr>
    </table>
    <ul>
      <li>Ejecut&eacute; los experimentos de l&iacute;nea base (Actividad E01) sobre un benchmark de <strong>30,000 registros crediticios</strong> (UCI Taiw&aacute;n, 22.12% default) evaluando Regresi&oacute;n Log&iacute;stica, XGBoost y MLP bajo <strong>validaci&oacute;n cruzada anidada 5&times;3</strong> y <strong>2,000 iteraciones bootstrap pareadas</strong> v&iacute;a CLI.</li>
      <li>Analic&eacute; m&eacute;tricas de desempe&ntilde;o <strong>respaldando el hallazgo emp&iacute;rico de que las representaciones num&eacute;ricas estructuradas superaron a los embeddings de texto enriquecidos con ontolog&iacute;as en el marco experimental evaluado</strong> (<strong>0.5596 AP en XGBoost</strong> frente a 0.5069 AP en representaci&oacute;n de texto R5).</li>
    </ul>

    <h2>Experiencia</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>Data Engineer Intern (Digital Solutions Specialist), GBM</strong> &ndash; San Salvador</td>
        <td class="right">Julio 2026 &ndash; Oct 2026</td>
      </tr>
    </table>
    <ul>
      <li>Dise&ntilde;&eacute; una <strong>propuesta de arquitectura ELT</strong> para replicaci&oacute;n en la nube casi en tiempo real en <strong>Google Cloud</strong> (<strong>BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage</strong>) entregando modelos dimensionales en <strong>Lucidchart</strong> y scripts <strong>SQL DDL</strong>.</li>
      <li>Desarroll&eacute; y ejecut&eacute; <strong>tareas pr&aacute;cticas de integraci&oacute;n ETL bajo mentor&iacute;a t&eacute;cnica</strong> en <strong>IBM InfoSphere DataStage</strong> (Transformers, Lookups, Joins, Merge, Funnel) sobre datasets de prueba empresariales y gestion&eacute; consultas en <strong>IBM DB2 LUW</strong> sobre <strong>Linux RHEL</strong>.</li>
      <li>Apoy&eacute; en la formulaci&oacute;n de marcos de gobernanza cloud y validaci&oacute;n presupuestaria FinOps (<strong>IAM</strong> de m&iacute;nimo privilegio, <strong>Service Accounts</strong>, rotaci&oacute;n de credenciales) y dimensionamiento de costos en <strong>Google Cloud Pricing Calculator</strong>.</li>
    </ul>

    <h2>Proyectos</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong><a href="https://github.com/bapatata688/Ferrostats">FERROSTATS</a> &mdash; Data Lakehouse Medall&oacute;n Cloud-Native y Pipeline Streaming en GCP</strong></td>
        <td class="right"><a href="https://github.com/bapatata688/Ferrostats">GitHub</a> &nbsp;|&nbsp; <a href="https://datastudio.google.com/reporting/2389e684-fc9b-431d-9c56-487b3067eb87/page/p_dwbfqrtk8d">Looker Studio BI</a> &nbsp;|&nbsp; <a href="https://ferrostats-bi-platform-s72yk4nsvq-uc.a.run.app">App en Vivo</a></td>
      </tr>
    </table>
    <ul>
      <li>Arquitect&eacute; un <strong>Data Lakehouse Medall&oacute;n (Bronze / Silver / Gold)</strong> en <strong>Google BigQuery</strong> con <strong>Dataform SQLX</strong>, transformando 4 tablas principales en Bronze hacia vistas Silver y <strong>3 Data Marts Gold en Esquema Estrella</strong> (<code>fct_daily_sales</code>, <code>mart_inventory_pareto_abc</code>, <code>dim_products</code>).</li>
      <li>Defin&iacute; especificaciones bajo <strong>Spec-Driven Development (SDD)</strong> para segmentaci&oacute;n Pareto ABC (80/20), Burn Rate y DOI, alimentando un dashboard ejecutivo de 3 p&aacute;ginas en <strong>Looker Studio</strong> con funciones de ventana anal&iacute;ticas.</li>
      <li>Especific&eacute; una arquitectura de ingesta desacoplada con <strong>streaming as&iacute;ncrono v&iacute;a REST API hacia BigQuery Bronze</strong>, estableciendo reglas de concurrencia transaccional e idempotencia por UUID bajo <strong>Spec-Driven Development (SDD)</strong>, y configur&eacute; una <strong>arquitectura FinOps (&lt;$1/mes) en GCP</strong> aprovechando la capa gratuita (Free Tier) en <strong>Cloud Run y BigQuery</strong>.</li>
    </ul>

    <h2>Habilidades</h2>
    <hr class="section-rule">
    <p class="skill-row"><strong>Cloud y Data Warehouses:</strong> Google Cloud Platform (BigQuery, Dataform SQLX, Datastream CDC, Cloud Storage, Cloud Run, Looker Studio, IAM Service Accounts, Cloud Logging/Monitoring, FinOps)</p>
    <p class="skill-row"><strong>Machine Learning y Modelado:</strong> Validaci&oacute;n Anidada (5x3 Nested CV), Bootstrap Resampling, XGBoost, Regresi&oacute;n Log&iacute;stica, BGE-M3 Embeddings, Evaluaci&oacute;n de Precisi&oacute;n Promedio (AP), Arquitectura Medallion</p>
    <p class="skill-row"><strong>Lenguajes y Herramientas:</strong> SQL (GoogleSQL, PostgreSQL 18, Window Functions, CTEs, DDL/DML), Python 3.11 (Pandas, PyArrow, NumPy), Bash, PowerShell, Docker, Linux RHEL, Git/SSH</p>
    <p class="skill-row"><strong>Idiomas:</strong> Espa&ntilde;ol (Nativo), Ingl&eacute;s (C1 Avanzado certificado por EF SET, 66/100, Listening C2 Proficient)</p>

    <h2>Certificaciones</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><a href="https://www.credly.com/badges/e27fea72-5eaf-47ee-a43c-43faa3a8fb10/public_url"><strong>Google Cloud Certified &mdash; Associate Data Practitioner</strong> (Cert ID: 23e3584a246f4c149f26fea03cebcbbb)</a></td>
        <td class="right">Oct 2026 &ndash; Oct 2029</td>
      </tr>
      <tr>
        <td class="left"><strong>Google Cloud Skill Badges: Derive Insights from Data &nbsp;|&nbsp; Prepare Data for Looker Dashboards and Reports</strong></td>
        <td class="right">Ago 2026</td>
      </tr>
      <tr>
        <td class="left"><a href="https://cert.efset.org/93nXaa"><strong>EF SET English Certificate &mdash; C1 Advanced</strong> (66/100 global &bull; Listening 75 C2 &bull; Speaking 69 C1)</a></td>
        <td class="right">Ene 2026</td>
      </tr>
      <tr>
        <td class="left"><strong>Code in Place (Python Programming) &mdash; Stanford University</strong></td>
        <td class="right">2026</td>
      </tr>
    </table>

    <h2>Educaci&oacute;n</h2>
    <hr class="section-rule">
    <table class="entry-header">
      <tr>
        <td class="left"><strong>University of the People</strong> &mdash; Pasadena, California, USA</td>
        <td class="right">Admitted | Term 3, 2027</td>
      </tr>
      <tr>
        <td class="left"><strong>Bachelor of Science in Computer Science</strong></td>
        <td class="right">WSCUC-accredited institution | 100% Online</td>
      </tr>
      <tr>
        <td class="left"><strong>Bachillerato T&eacute;cnico Vocacional en Desarrollo de Software</strong> &ndash; Instituto Nacional San Luis &nbsp;|&nbsp; <em>Promedio: 9.5/10.0</em></td>
        <td class="right">2026</td>
      </tr>
    </table>
  </main>"""


@dataclass
class CVTarget:
    """Target configuration for a single CV compilation target."""
    id: str
    track: str
    lang: str
    title: str
    html_rel_path: Path
    pdf_rel_path: Path
    body_html: str
    css_params: CSSParameters = field(default_factory=CSSParameters)

    def full_html(self) -> str:
        css = self.css_params.render_css()
        return f"""<!DOCTYPE html>
<html lang="{self.lang}">
<head>
  <meta charset="utf-8">
  <title>{self.title}</title>
  <style>{css}</style>
</head>
<body>
{self.body_html}
</body>
</html>
"""


TARGETS: List[CVTarget] = [
    CVTarget(
        id="de_en",
        track="01_produccion_data_engineering",
        lang="en",
        title="Diego Alejandro Escobar Barahona - CV (EN)",
        html_rel_path=Path("cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.html"),
        pdf_rel_path=Path("cv/01_produccion_data_engineering/en/Diego_Alejandro_Escobar_Barahona_CV_EN.pdf"),
        body_html=HTML_BODY_DE_EN,
    ),
    CVTarget(
        id="de_es",
        track="01_produccion_data_engineering",
        lang="es",
        title="Diego Alejandro Escobar Barahona - CV (ES)",
        html_rel_path=Path("cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.html"),
        pdf_rel_path=Path("cv/01_produccion_data_engineering/es/Diego_Alejandro_Escobar_Barahona_CV_ES.pdf"),
        body_html=HTML_BODY_DE_ES,
    ),
    CVTarget(
        id="pub_en",
        track="02_publicacion_ia_investigacion",
        lang="en",
        title="Diego Alejandro Escobar Barahona - CV EN (Publications)",
        html_rel_path=Path("cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.html"),
        pdf_rel_path=Path("cv/02_publicacion_ia_investigacion/en/Diego_Alejandro_Escobar_Barahona_CV_EN_Publications.pdf"),
        body_html=HTML_BODY_PUB_EN,
    ),
    CVTarget(
        id="pub_es",
        track="02_publicacion_ia_investigacion",
        lang="es",
        title="Diego Alejandro Escobar Barahona - CV ES (Publicaciones)",
        html_rel_path=Path("cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.html"),
        pdf_rel_path=Path("cv/02_publicacion_ia_investigacion/es/Diego_Alejandro_Escobar_Barahona_CV_ES_Publicaciones.pdf"),
        body_html=HTML_BODY_PUB_ES,
    ),
]

TARGETS_BY_ID: Dict[str, CVTarget] = {t.id: t for t in TARGETS}


def resolve_weasyprint_cli() -> Optional[str]:
    """Finds the weasyprint CLI executable on Windows or Linux."""
    exe = shutil.which("weasyprint")
    if exe:
        return exe

    # Windows Scoop fallback paths
    candidates = [
        Path.home() / "scoop" / "shims" / "weasyprint.exe",
        Path(r"C:\Users\Usuario\scoop\shims\weasyprint.exe"),
        Path(r"C:\Users\Usuario\scoop\apps\weasyprint\current\weasyprint.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def compile_pdf_with_weasyprint(
    html_path: Path,
    pdf_path: Path,
    engine: str = "auto",
    verbose: bool = False,
) -> None:
    """
    Compiles an HTML file to PDF using WeasyPrint with atomic temporary writes.
    Supports 'auto', 'cli', and 'python' engines.
    """
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_pdf = pdf_path.parent / f".tmp_{uuid.uuid4().hex[:8]}_{pdf_path.name}"

    try:
        # Determine strategy
        use_python = False
        if engine == "python":
            use_python = True
        elif engine == "cli":
            use_python = False
        else:  # auto
            # On Windows, native import usually fails due to GTK DLL path isolation in Scoop.
            # On Linux / macOS, native import is faster and cleaner.
            if sys.platform == "win32":
                use_python = False
            else:
                use_python = True

        compiled = False
        if use_python:
            try:
                from weasyprint import HTML
                HTML(filename=str(html_path)).write_pdf(str(tmp_pdf))
                compiled = True
            except (ImportError, OSError) as e:
                if engine == "python":
                    raise RuntimeError(f"Native python weasyprint import failed: {e}")
                if verbose:
                    print(f"  [i] Native weasyprint import failed ({e}), falling back to CLI...")

        if not compiled:
            cli_path = resolve_weasyprint_cli()
            if not cli_path:
                raise FileNotFoundError(
                    "weasyprint executable not found in PATH or Scoop shims. "
                    "Install via Scoop ('scoop install weasyprint') or apt-get on Linux."
                )
            cmd = [cli_path, str(html_path), str(tmp_pdf)]
            if verbose:
                print(f"  [>] Invoking: {' '.join(cmd)}")
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(
                    f"WeasyPrint CLI failed with exit code {res.returncode}:\n"
                    f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
                )

        if not tmp_pdf.exists() or tmp_pdf.stat().st_size == 0:
            raise RuntimeError(f"Compiled PDF was not created or is empty: {tmp_pdf}")

        # Atomic replacement on destination
        try:
            os.replace(tmp_pdf, pdf_path)
        except PermissionError as perm_err:
            raise PermissionError(
                f"Cannot overwrite {pdf_path}: file may be locked by a PDF reader. "
                f"Please close Adobe Acrobat / viewer and retry. Details: {perm_err}"
            )

    except Exception:
        if tmp_pdf.exists():
            try:
                tmp_pdf.unlink()
            except Exception:
                pass
        raise


def compile_all(
    targets: Optional[List[str]] = None,
    base_dir: Optional[Path] = None,
    html_only: bool = False,
    pdf_only: bool = False,
    engine: str = "auto",
    verbose: bool = False,
) -> List[Path]:
    """
    Build orchestrator for master_cv.
    Returns list of compiled PDF paths.
    """
    if base_dir is None:
        # Default to repo root (parent of cv/ directory)
        base_dir = Path(__file__).resolve().parent.parent

    selected_targets: List[CVTarget] = []
    if not targets or "all" in targets:
        selected_targets = TARGETS
    else:
        for tid in targets:
            if tid not in TARGETS_BY_ID:
                raise ValueError(f"Unknown target ID '{tid}'. Valid choices: {list(TARGETS_BY_ID.keys())}")
            selected_targets.append(TARGETS_BY_ID[tid])

    compiled_pdfs: List[Path] = []

    for target in selected_targets:
        html_path = base_dir / target.html_rel_path
        pdf_path = base_dir / target.pdf_rel_path

        html_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        if not pdf_only:
            html_content = target.full_html()
            html_path.write_text(html_content, encoding="utf-8")
            if verbose:
                print(f"[HTML] Written: {html_path.relative_to(base_dir)}")

        if not html_only:
            if verbose:
                print(f"[PDF] Compiling: {target.id} -> {pdf_path.name}...")
            compile_pdf_with_weasyprint(html_path, pdf_path, engine=engine, verbose=verbose)
            size_kb = pdf_path.stat().st_size / 1024
            print(f"[OK] {target.id.upper()}: {pdf_path.relative_to(base_dir)} ({size_kb:.1f} KB)")
            compiled_pdfs.append(pdf_path)

    return compiled_pdfs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compile master_cv documents with WeasyPrint.")
    parser.add_argument("--target", "-t", nargs="*", default=["all"], help="Target IDs (de_en, de_es, pub_en, pub_es, all)")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML templates without compiling PDFs")
    parser.add_argument("--pdf-only", action="store_true", help="Compile PDFs from existing HTML templates")
    parser.add_argument("--engine", choices=["auto", "cli", "python"], default="auto", help="WeasyPrint execution engine")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    try:
        compile_all(
            targets=args.target,
            html_only=args.html_only,
            pdf_only=args.pdf_only,
            engine=args.engine,
            verbose=args.verbose,
        )
    except Exception as exc:
        print(f"[ERROR] Compilation failed: {exc}", file=sys.stderr)
        sys.exit(1)
