# HealthyMed: custom field list (the senior's build)

Source: read-only discovery of the senior's system. Field name, type, label.
Fields on product.template also appear on product.product. Fields on
res.partner also appear on res.users. Labels are German and are used for
i18n\de.po. The base language of the source strings is English.

Build order: base, rollen, ssb, chargen, megro_import, pricing, shop,
rezept_kv, megro_dropship, theme.

## healthymed_base
product.template
| Field | Type | Label |
|---|---|---|
| x_ean | Char | EAN |
| x_magento_id | Char | Magento ID |
| x_manufacturer | Char | Hersteller |
| x_packaging_unit | Char | Verpackungseinheit |
| x_qty_unit | Char | Mengeneinheit |

res.partner
| x_is_regional | Boolean | Regionalkunde (Eigenbelieferung) |

sale.order
| x_is_regional_order | Boolean (related, readonly) | Regionale Eigenbelieferung |

res.company
| x_regional_warehouse_id | Many2one stock.warehouse | Lager für Eigenbelieferung |
| x_supplier_warehouse_id | Many2one stock.warehouse | Lager für Lieferantenabwicklung |

## healthymed_rollen
No custom fields. Security groups only. See rollen-groups.md.

## healthymed_ssb
product.template
| x_is_ssb | Boolean | Sprechstundenbedarf (SSB) |
| x_pzn | Char | PZN |

res.partner
| x_praxis_nr | Char | Praxis-Nr. (SSB) |
| x_kv_nummer | Char | KV-Nummer |

res.company
| x_ssb_gate_enabled | Boolean | SSB-Rezept-Gate aktiv |

res.config.settings
| x_ssb_gate_enabled | Boolean (related to company) | SSB-Rezept-Fulfillment-Gate |

sale.order
| x_has_ssb | Boolean (computed, stored) | Enthält SSB-Artikel |
| x_ssb_prescription_file | Binary | Rezept-Scan (optional) |
| x_ssb_prescription_filename | Char | Rezept-Dateiname |
| x_ssb_prescription_received_by | Many2one res.users (readonly) | Rezept bestätigt von |
| x_ssb_prescription_received_date | Datetime (readonly) | Rezepteingang am |
| x_ssb_prescription_state | Selection: not_required / waiting / received | SSB-Rezeptstatus |

## healthymed_chargen
No custom fields. Configuration on top of standard product_expiry only.

## healthymed_megro_import
product.template
| x_is_megro_article | Boolean | Megro-Sortiment |
| x_megro_available | Boolean | Megro verfügbar |
| x_megro_mb | Integer | Megro Mindestbestand |
| x_megro_stock_date | Char (not Date) | Megro Bestand Stand |

healthymed.megro.feed (new model)
| name | Char, required | Bezeichnung |
| active | Boolean | Active |
| partner_id | Many2one res.partner | Lieferant |
| delimiter | Selection: ; / , / tab | Trennzeichen |
| encoding | Selection: utf-8-sig / cp1252 | Zeichensatz |
| has_header | Boolean | Mit Kopfzeile |
| match_field | Selection: default_code / x_pzn / barcode | Zuordnung über |
| create_missing | Boolean | Unbekannte Artikel anlegen |
| update_price | Boolean | Einkaufspreis aktualisieren |
| update_availability | Boolean | Verfügbarkeit aktualisieren |
| update_sale_price | Boolean | Verkaufspreis aktualisieren |
| stale_after_days | Integer | Warnen nach Tagen ohne Lieferung |
| last_attachment_id | Many2one ir.attachment (readonly) | Zuletzt eingelesene Datei |
| last_run | Datetime (readonly) | Zuletzt gelaufen |
| last_result | Char (readonly) | Ergebnis |
| column_ids | One2many healthymed.megro.feed.column | Spaltenzuordnung |
| log_ids | One2many healthymed.megro.import.log (readonly) | Protokoll |

healthymed.megro.feed.column (new model)
| feed_id | Many2one healthymed.megro.feed, required | Feed |
| sequence | Integer | Sequence |
| source | Char, required | Spalte in der Datei |
| target | Selection: default_code, x_pzn, barcode, name, standard_price, list_price, x_megro_available, x_megro_mb, x_manufacturer, x_packaging_unit, supplier_code | Odoo-Feld |

healthymed.megro.import.log (new model)
| feed_id | Many2one healthymed.megro.feed, required | Feed |
| rows | Integer | Zeilen |
| matched | Integer | Zugeordnet |
| created | Integer | Angelegt |
| updated | Integer | Aktualisiert |
| skipped | Integer | Übersprungen |
| unmatched | Integer | Ohne Treffer |
| unmatched_sample | Char | Beispiele ohne Treffer |

## healthymed_pricing
No custom fields or models. Standard product.pricelist and
product.pricelist.item configuration only.

## healthymed_shop
delivery.carrier
| x_free_over_untaxed | Boolean | Schwelle auf Nettobetrag anwenden |

payment.provider
| custom_mode | Selection, extends the existing field with: wire_transfer, cash_on_delivery, invoice | Custom Mode |

product.template
| x_speditionsversand | Boolean | Speditionsversand |

res.company
| x_min_order_amount | Monetary | Mindestbestellwert (netto) |

res.partner
| x_invoice_allowed | Boolean (readonly) | Rechnungskauf möglich |
| x_invoice_approved | Boolean | Bonitätsprüfung bestanden |

res.partner.industry
| x_invoice_without_credit_check | Boolean | Rechnungskauf ohne Bonitätsprüfung |

sale.order
| x_amount_untaxed_without_delivery | Monetary (computed, readonly) | Nettowarenwert (ohne Versand) |
| x_below_min_order | Boolean (computed, readonly) | Unter Mindestbestellwert |

healthymed.return.reason (new model)
| name | Char, required | Grund |
| sequence | Integer | Reihenfolge |
| note_required | Boolean | Anmerkung verlangen |
| active | Boolean | Aktiv |

healthymed.return.request (new model)
| reference | Char, required, readonly (sequence) | Vorgang |
| order_id | Many2one sale.order | Auftrag |
| order_ref | Char, required | Auftragsnummer |
| partner_id | Many2one res.partner | Kunde |
| partner_ref | Char, required | Kundennummer |
| email | Char, required | E-Mail-Adresse |
| product_code | Char | Artikelnummer |
| reason_id | Many2one healthymed.return.reason, required | Grund |
| condition | Selection: sealed / opened | Zustand |
| note | Text | Anmerkung |
| state | Selection: new / review / approved / rejected / done | Status |
Also carries mail.thread, mail.activity.mixin and rating.mixin fields. The
reference field needs an ir.sequence record.

## healthymed_rezept_kv
healthymed.kv.region (new model)
| name | Char, required | Name |
| code | Char, required | Code |
| active | Boolean | Active |
| kostentraeger_name | Char | Kostentraeger |
| ik_number | Char | Kostentraegerkennung (IK) |
| ik_preprinted | Boolean | IK bereits vorgedruckt |
| ik_overprint_allowed | Boolean | Ueberdrucken der IK zulaessig |
| form_template | Selection: muster_16 / muster_16a / portal | Formular |
| form_width_mm | Float | Formularbreite (mm) |
| form_height_mm | Float | Formularhöhe (mm) |
| paperformat_id | Many2one report.paperformat | Papierformat |
| lines_x_mm | Float | Verordnungen X (mm) |
| lines_y_mm | Float | Verordnungen Y (mm) |
| lines_width_mm | Float | Verordnungen Breite (mm) |
| lines_height_mm | Float | Zeilenabstand (mm) |
| max_positions | Integer | Max. Positionen je Rezept |
| field9_mode | Selection: print_digit / preprinted / mark_x / unclear | Feld 9 |
| patient_data_forbidden | Boolean | Ohne Patientendaten |
| separate_per_category | Boolean | Getrennte Verordnungen je Kategorie |
| ssb_label | Char | Aufdruck / Bezeichnung |
| supported | Boolean | Vom Generator unterstuetzt |
| is_calibrated | Boolean, readonly | Kalibriert |
| note | Text | Hinweise |
| field_ids | One2many healthymed.rezept.field | Feldpositionen |

healthymed.rezept.field (new model)
| region_id | Many2one healthymed.kv.region, required | KV-Region |
| key | Selection: kostentraeger_name, kostentraeger_ik, bsnr, lanr, datum, field9, ssb_label, praxis_aufdruck | Key |
| x_mm | Float, required | X (mm) |
| y_mm | Float, required | Y (mm) |
| font_size_pt | Float | Schriftgröße (pt) |
| bold | Boolean | Fett |
| calibrated | Boolean | Kalibriert |
| note | Char | Hinweis |

res.partner
| x_bsnr | Char, size 9 | BSNR (Betriebsstättennummer) |
| x_lanr | Char, size 9 | LANR (Lebenslange Arztnummer) |
| x_kv_region_id | Many2one healthymed.kv.region | KV-Region |
| x_kostentraeger_ik | Char | Kostenträgerkennung (abweichend) |

Also an ir.actions.report record (QWeb PDF report) with its template. No new
fields on that model.

## healthymed_megro_dropship
healthymed.megro.order.config (new model)
| name | Char, required | Name |
| active | Boolean | Active |
| company_id | Many2one res.company, required | Company |
| partner_id | Many2one res.partner | Lieferant |
| recipient | Char | Empfänger |
| subject_template | Char | Betreff |
| delimiter | Selection: ; / , / tab | Delimiter |
| attach_csv | Boolean | CSV anhängen |
| column_ids | One2many healthymed.megro.order.column | Spalten |

healthymed.megro.order.column (new model)
| config_id | Many2one healthymed.megro.order.config, required | Config |
| sequence | Integer | Sequence |
| header | Char, required | Spaltenüberschrift |
| source | Selection: supplier_code, default_code, pzn, barcode, name, qty, order_ref, delivery_name, delivery_street, delivery_zip, delivery_city | Inhalt |

sale.order
| x_megro_sent_by | Many2one res.users, readonly | Übermittelt von |
| x_megro_sent_on | Datetime, readonly | An Megro übermittelt |
| x_regional_forward_ok | Boolean, readonly | Weiterleitung an Megro freigegeben |
| x_regional_forward_by | Many2one res.users, readonly | Weiterleitung freigegeben von |
| x_regional_forward_on | Datetime, readonly | Weiterleitung freigegeben am |

## healthymed_theme
sale.order
| x_hm_ordered_by | Char | Bestellt von |
| x_hm_warehouse_note | Char | Hinweis für unser Lager |
Everything else in this module is views, QWeb and assets, not fields.

## Open items
1. x_megro_stock_date is Char, not Date, on the senior's system. Keep it Char
   and log it as a known compromise.
2. healthymed.return.request.reference needs an ir.sequence record.
3. The group names behind the role IDs are unresolved (see rollen-groups.md).
4. Unknown: what x_is_regional_order is related to (assume partner_id until
   confirmed), the rule that computes x_invoice_allowed, and whether
   rating.mixin on return requests is intentional.