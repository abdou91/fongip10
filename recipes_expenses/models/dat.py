# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from datetime import datetime


PAYMENT_FREQUENCY = [
							('mensuelle', "Mensuelle"), 
                            ('trimestrielle', "Trimestrielle"), 
                            ('semestrielle',"Semestrielle"),
                            ('annuelle', "Annuelle"),
                        ]

class DAT(models.Model):
	_name = 'bank.dat'
	_description = 'DAT'

	name = fields.Char(string = "Libellé", required = True)
	bank_account_id = fields.Many2one('res.partner.bank',string = "Compte bancaire")
	bank_id = fields.Many2one('res.bank',string = "Banque")
	duration = fields.Integer(string = "durée")
	rate = fields.Float(string = "Taux brut")
	value_of_date = fields.Date(string = "Date de valeur")#date à partir de laquelle les echeances sont calculées
	maturity_of_date = fields.Date(string = "Date de maturité")
	payment_frequency = fields.Selection(PAYMENT_FREQUENCY, default = "mensuelle", string = "Périodicité de versement")
	currency_id = fields.Many2one(
        'res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id
    )
	amount = fields.Monetary(string = "Montant")
	interest = fields.Monetary(string = "Intérêt") #cumul des interets
	outstanding_amount = fields.Monetary(string = "Encours")
	released_amount = fields.Monetary(string = "Montant débloqué")
	
	contract_id = fields.Many2one(
		'contract',
		string = "Convention DAT",
		domain="[('type_id_code','=','cdat')]"
		)

	@api.onchange('bank_account_id')
	def _onchange_bank_account_id(self):
		if self.bank_account_id:
			self.bank_id = self.bank_account_id.bank_id.id

#operations sur les DAT deblocage et renumeration
#renumeration : date_echeance
#deblocage : montant debloque,date de deblocage,
class DatInterest(models.Model):
	_name = 'bank.dat.interest'
	_description = 'Interets'

	dat_id = fields.Many2one('bank.dat',string = "DAT")
	date_echeance = fields.Date(string = "Date d'échéance")
	number_of_days = fields.Integer(string = "Nombre de jours")
	#interet_trim_recalcule = encours_dat * taux * number_of_days / 365 
	#retraitement_tva = interet_trim_recalcule / 1.18
	#montant_irc_recalcule = retraitement_tva * 8%
	#montant_tva = retraitement_tva * 18%
	#interet_net_sans_tva_et_irc = retraitement_tva - montant_irc_recalcule
	#interet_net_irc_tva = interet_net_sans_tva_et_irc  + montant_tva + montant_irc_recalcule
	currency_id = fields.Many2one(
        'res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id
    )
	interest_paid_by_the_bank = fields.Monetary(string = "Intérêt versé par la banque")
	diff_interest = fields.Monetary(string = "INTERETS  / TRIM  RECALCULES  -  INT VERSES PAR LA BANQUE")
	irc_retained_by_the_bank = fields.Monetary(string = "IRC retenu par la banque")
	diff_irc = fields.Monetary(string = "Montant IRC RECALCULES -  NT VERSES PAR LA BANQUE")

