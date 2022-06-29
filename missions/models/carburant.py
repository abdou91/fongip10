# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


TYPE_CARTE_CARBURANT = [
								('mission','MISSION'),
								('personnel','PERSONNEL'),
						]

class CarteCarburant(models.Model):
	_name = 'carte.carburant'
	_description = 'Model de carte de carburant'
	_order = 'numero_carte asc'

	name = fields.Char(string="Libellé")
	numero_carte = fields.Char(string="Numéro carte",required=True)
	detenteur = fields.Many2one('hr.employee',string="Détenteur de la carte ")
	fournisseur = fields.Many2one('res.partner',string="Fournisseur")#,domain="[('supplier','=',True)]"
	chargement_carte_ids = fields.One2many('carte.chargement','carte_carburant',string="Chargements")
	#*****************************
	quantite_charge = fields.Integer(string="Quantité Chargée",compute="_compute_total_chargement",store=True)
	quantite_consomme = fields.Integer(string="Quantité consommée",compute="_compute_total_consommation",store=True)
	quantite_restante = fields.Integer(string="Quantité consommée",compute="_compute_total",store=True)
	consommation_carte_ids = fields.One2many('fleet.vehicle.log.fuel','carte_carburant',string="Consommations")
	cout_chargement = fields.Float(string = "Cout chargement",digits=(12,0),compute="_compute_total_chargement",store=True)
	cout_consommation = fields.Float(string = "Cout consommation",digits=(12,0),compute="_compute_total_consommation",store=True)
	#****************************
	#quantite = fields.Integer(string="Quantité Totale",compute="_compute_total",store=True)
	#bon_carburant_ids = fields.One2many('fleet.vehicle.log.fuel','carte_carburant','Bons de carburant')
	#consommation = fields.Integer(string="Nombre de litres consommés",compute="_compute_consommation",store=True)
	quantite_actuelle = fields.Integer(string="Quantité actuelle", compute="_compute_quantite_actuelle",store=True)#,compute="_compute_quantite",store=True
	#montant_consommation = fields.Float(string="Montant consommation",digits=(12,0),compute="_compute_consommation",store=True)
	montant = fields.Float(string="Montant",digits=(12,0),compute="_compute_total",store=True)
	color = fields.Integer(string = 'Color Index', default = 0)
	type_carte = fields.Selection(TYPE_CARTE_CARBURANT,'Type de carte',default='personnel')

	_sql_constraints = [('numero_carte_unique', 'unique (numero_carte)', "Ce numéro de carte existe déja, merci de choisir un autre numéro de carte")]
	
	@api.depends('chargement_carte_ids')
	def _compute_total_chargement(self):
		self.quantite_charge = sum(self.chargement_carte_ids.mapped('quantite'))
		self.cout_chargement = sum(self.chargement_carte_ids.mapped('montant'))

	@api.depends('consommation_carte_ids')
	def _compute_total_consommation(self):
		self.quantite_consomme = sum(self.consommation_carte_ids.mapped('liter'))
		self.cout_consommation = sum(self.consommation_carte_ids.mapped('cost_amount'))

	"""@api.depends('chargement_carte_ids')
	def _compute_total(self):
		if self.chargement_carte_ids:
			self.quantite = sum(self.chargement_carte_ids.mapped('quantite'))
			self.montant = sum(self.chargement_carte_ids.mapped('montant'))
			#self.montant_consommation = sum(self.chargement_carte_ids.mapped())"""

	@api.depends('quantite_charge','quantite_consomme')
	def _compute_quantite_actuelle(self):
		self.quantite_actuelle = self.quantite_charge - self.quantite_consomme
		"""if self.quantite and not self.consommation:
			self.quantite_actuelle = self.quantite
		elif self.quantite and self.consommation:
			self.quantite_actuelle = self.quantite - self.consommation"""
		


	"""@api.depends('bon_carburant_ids')
	def _compute_consommation(self):
		if self.bon_carburant_ids:
			self.consommation = sum(self.bon_carburant_ids.mapped('liter'))
			self.montant_consommation = sum(self.bon_carburant_ids.mapped('cost_amount'))"""



class ChargementCarte(models.Model):
	_name = 'carte.chargement'
	_description = 'Chargement de carte'
	_rec_name = 'carte_carburant'
	carte_carburant = fields.Many2one('carte.carburant',string="Carte",ondelete="cascade")
	date = fields.Date(string="Date ")
	quantite = fields.Integer(string="Nombre de litres")
	prix_unitaire = fields.Float(string="Prix au litre",digits=(4,0),default=775)
	montant = fields.Float(string="Montant",digits=(12,0),compute="_compute_montant",store=True)


	@api.depends('quantite','prix_unitaire')
	def _compute_montant(self):
		for record in self:
			if record.quantite and record.prix_unitaire:
				record.montant = record.quantite * record.prix_unitaire

