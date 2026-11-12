# ActionRelay Forms & Resources

This directory contains short, clearly labeled synthetic employee resources for the local ActionRelay presentation build. The workplace guide is five pages. The directory uses only synthetic names, example.com email addresses, and fictitious 555-01xx numbers.

## Synthetic sample PDFs

- `synthetic-workplace-guide.pdf` — fictional general workplace guide; not actual CDIT policy.
- `synthetic-company-directory.pdf` — fictional supervisory/support contacts and a catalog of available forms.
- `synthetic-vacation-request.pdf` — blank general request form; a request is not approval.
- `synthetic-workplace-complaint.pdf` — blank general workplace concern form; not a legal filing or confidential hotline.
- Existing synthetic employee resources remain in `docs/presentations/ActionRelay/`: the weekly timesheet PDF and the sample shift-pattern/change-request PDF. Both are also listed in the shared footer and directory catalog.

Regenerate these files with `python tools/build_synthetic_resources.py`. The source content and layout are maintained in that script.

## Official blank forms

The app links directly to the issuing agencies' current PDFs/pages rather than copying or editing official forms:

- IRS Form W-4: <https://www.irs.gov/pub/irs-pdf/fw4.pdf>
- U.S. Department of Labor WH-380-E: <https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-e.pdf>
- U.S. Department of Labor WH-380-F: <https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-f.pdf>
- NY Paid Family Leave family-care package (PFL-1/PFL-3/PFL-4): <https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL3.pdf>
- NY Paid Family Leave forms page: <https://paidfamilyleave.ny.gov/forms>
- NYC IDNYC application materials: <https://www.nyc.gov/site/idnyc/card/application-materials.page>

## Personal-document boundary

The current local build is synthetic-only and does not accept or transmit personal-document uploads. Do not upload real identity, medical, tax, payroll, or work-authorization records. A live workflow must route a document only to its responsible department, exclude the file from automated processing and ticket records, and fail closed if its approved secure department destination is unavailable. Department identity, access, transmission, retention, incident handling, file scanning, and audit controls require implementation and review before live personal documents are accepted.

If user-generated resources are later added, they must be labeled as user-generated and reviewed before being presented as official.
