# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import Warning, ValidationError
from datetime import datetime , timedelta
from dateutil.relativedelta import relativedelta



TYPE_MISSIONNAIRE = [
				('ag','AG ou DG'),
				('agent','AGENT'),
		   ]
TYPE_MISSION = [
					('interieur','Interieur'),
					('exterieur','exterieur'),
				]

MOYEN_TRANSPORT = [
						('voiture','Voiture'),
						('bateau','Bateau'),
						('train','Train'),
						('avion','Avion'),
				  ]
PRISE_EN_CHARGE = [
						('carburant','Carburant'),
						('perdieme','Perdieme'),
						('carburant_perdieme','Carburant / Perdieme'),
					]

SOURCE = [
				('carte','Carte'),
				('ticket','Ticket'),
		 ]

TYPE_CARTE_CARBURANT = [
								('mission','MISSION'),
								('personnel','PERSONNEL'),
						]
  




#****************************Mission**********************
"""class VehicleMission(models.Model):
	_name = 'vehicle_mission'
	_description = "Vehicle mission"
	vehicle_id = fields.Many2one('fleet.vehicle',string='Véhicule',ondelete='cascade')
	#conducteur = fields.Char(related='vehicle_id.driver_id.name', string='Conducteur', store=True)
	conducteur = fields.Many2one('hr.employee',string="Conducteur")#,domain=[('est_chauffeur','=','oui')]
	mission_id = fields.Many2one('mission',string='Mission' , ondelete='cascade')
	price_per_liter = fields.Float(default=775, string = "Prix au litre")
	liter = fields.Float(string = "Litre")
	amount = fields.Float(string = "Prix total",compute='_compute_amount',store=True)

	@api.depends('liter','price_per_liter')
	def _compute_amount(self):
		for record in self:
			if record.liter and record.price_per_liter:
				record.amount = record.liter * record.price_per_liter
"""



class RangHierarchique(models.Model):
	_name = 'rang.hierarchique'
	_description = 'Rang hierarchique'
	name = fields.Char(string = "Rang hierarchique")


class Missionnaire(models.Model):
	_name = 'missionnaire'
	_description = "Missionnaire"
	#_inherit = ['mail.thread', 'ir.needaction_mixin']
	mission_id = fields.Many2one('mission' , string='Mission' , ondelete='cascade')
	employee_id = fields.Many2one('hr.employee', string="Employé" , ondelete='cascade')
	titre_poste = fields.Char(related='employee_id.job_id.name',string='Titre du poste',store=True)
	first_name = fields.Char(string='Prénom')
	last_name = fields.Char(string='Nom')
	numero_ordre = fields.Integer(string="Numéro")
	numero_missionnaire = fields.Char(string="OM N°" ,compute="_compute_numero_missionnaire",store=True)
	montant_avance = fields.Integer(string="Montant avancé" ) #, compute="_compute_perdium" , store=True"""
	montant_restant = fields.Integer(string="Montant restant à payer" ) #, compute="_compute_perdium" , store=True"""
	indemnite_journaliere = fields.Integer(string="Indemnité journalière " ) #,compute="_compute_perdium" , store=True"""
	montant_total = fields.Float(string = "Montant total", compute='_compute_montant_total', store = True)
	visible = fields.Boolean(default=True)
	rang_hierarchique_id = fields.Many2one('rang.hierarchique',string="Rang hierarchique")
	#type_missionnaire = fields.Selection(TYPE_MISSIONNAIRE,string = "Type missionnaire",default="agent")
	#type_missionnaire = fields.Many2one('type.missionnaire',string="Type missionnaire",required=True)
	prise_en_charge = fields.Selection(PRISE_EN_CHARGE,'Prise en charge',default='perdieme')
	visible = fields.Boolean(default=True)

	"""@api.model
	def default_get(self,fields):
		res = super(Missionnaire,self).default_get(fields)
		type_missionnaire = self.env['type.missionnaire'].search([('name','like','AGENT')],limit=1)
		if 'type_missionnaire' in fields and type_missionnaire:
			res.update({
				'type_missionnaire':type_missionnaire.id,
				'prise_en_charge':'perdieme',
				}) 
		return res"""

	@api.model
	def create(self,vals):
		if 'mission_id' in vals and vals['mission_id']:
			numero_ordre = self.search([('mission_id','=',vals['mission_id'])],order='numero_ordre desc', limit=1).numero_ordre
			if numero_ordre >= 0:
				vals['numero_ordre'] = numero_ordre + 1
			else:
				vals['numero_ordre'] = 0
		return super(Missionnaire,self).create(vals)


	@api.depends('numero_ordre')
	def _compute_numero_missionnaire(self):
		for record in self:
			if record.numero_ordre >=0 and record.mission_id:
				record.numero_missionnaire = (4-len(str(record.numero_ordre)))*'0'+str(record.numero_ordre) +'/'+ str(record.mission_id.numero_mission)
				
	
	@api.depends('montant_avance','montant_restant')
	def _compute_montant_total(self):
		for record in self:
			record.montant_total = record.montant_avance + record.montant_restant

	@api.onchange('rang_hierarchique_id')
	def onchange_perdium(self):
		for record in self:
			if record.mission_id and record.rang_hierarchique_id and record.employee_id and record.mission_id.zone:
				if record.mission_id.nombre_nuites and record.mission_id.type_mission:
					indemnite = self.env['mission.indemnite.journaliere'].search([('zone','=',record.mission_id.zone.id),('rang_hierarchique_id','=',record.rang_hierarchique_id.id)],limit=1)
					if indemnite:
						record.indemnite_journaliere = indemnite.montant
						if record.mission_id.perdium_mode_payment_id:
							if record.mission_id.perdium_mode_payment_id.mode_payment == 'paiement_partiel':
								record.visible = True
								if record.mission_id.perdium_mode_payment_id.pourcentage.__contains__('/'):
									liste = record.mission_id.perdium_mode_payment_id.pourcentage.strip().split('/')
									numerateur,denominateur = int(liste[0].strip()),int(liste[1].strip())
									record.montant_avance = round((record.mission_id.nombre_nuites * indemnite.montant * numerateur) / denominateur)
									record.montant_restant = record.mission_id.nombre_nuites * indemnite.montant - record.montant_avance
									#record.montant_total = record.montant_avance + record.montant_restant
							else:
								record.visible = False
								record.montant_avance = record.mission_id.nombre_nuites * indemnite.montant
								record.montant_restant = 0



	@api.onchange('employee_id')
	def _employee_id(self):
		if self.employee_id:
			liste = str(self.employee_id.name).split(' ')
			self.last_name = liste[-1]
			self.first_name = " ".join(liste[:-1])

	
	"""@api.onchange('montant_avance')
	def onchange_montant_avance(self):
		self.montant_restant = self.mission_id.nombre_nuites * self.indemnite_journaliere - self.montant_avance
	"""



	"""def action_print_ordre_mission(self):
		return self.env.ref('missions.report_ordre_mission').report_action(self)"""

class PerdiumPayment(models.Model):
	_name = 'perdium.mode.payment'
	_description = 'Perdium mode payment'

	type_mission = fields.Selection(TYPE_MISSION,string='Type',default='interieur', required = True)
	mode_payment = fields.Selection([('paiement_partiel','Paiement partiel'),('paiement_total','Paiement total')],default="paiement_total",string="Conditions de paiement du perdium")
	pourcentage = fields.Char(string = "Pourcentage",help="format du pourcentage a/b")
	

class MissionType(models.Model):
	_name = 'mission.type'
	_description = 'Type de mission'
	name = fields.Char(string='Libellé')
	payment_perdium = fields.Selection([('paiement_partiel','Paiement partiel'),('paiement_total','Paiement total')],default="paiement_total",string="Conditions de paiement du perdium")
	pourcentage = fields.Char(string = "Pourcentage",help="format du pourcentage a/b")
	#avance_numerateur = fields.Float(string="Numérateur")
	#avance_denominateur = fields.Float(string="Dénominateur")
	#montant = fields.Integer(string='Montant indemnité journalière')
	#zone_id = fields.Many2one('mission.zone',string="Zone")

	@api.onchange('zone_id')
	def onchange_zone(self):
		if self.zone_id:
			self.montant = 1 

class ZoneMission(models.Model):
	_name = 'mission.zone'
	_description = "Zone"
	name = fields.Char(string="Zone")
	description = fields.Text(string="Description")
	#montant = fields.Integer(string="Montant indemnité journalière")

	_sql_constraints = [('name_unique', 'unique (name)', "Ce nom de zone existe déjà, merci de choisir un autre nom de zone")]

"""class TypeMissionnaire(models.Model):
	_name = 'type.missionnaire'
	name = fields.Char(string="Type missionnaire")

	_sql_constraints = [('name_unique', 'unique (name)', "Ce Type de missionnaire  existe déjà, merci de choisir un autre type de missionnaire")]"""

class IndemniteJournaliere(models.Model):
	_name = 'mission.indemnite.journaliere'
	_description = "indemnite journaliere des mission"
	zone = fields.Many2one('mission.zone',string="Zone",required = True)
	rang_hierarchique_id = fields.Many2one('rang.hierarchique',string="Rang hierarchique")
	#type_missionnaire = fields.Selection(TYPE_MISSIONNAIRE,string = "Type missionnaire",default="agent",required = True)
	#type_mission = fields.Selection(TYPE_MISSION,string='Type',default='interieur',required = True)
	montant = fields.Integer(string="Montant",required = True)

class Mission(models.Model):
	_name="mission"
	_description = "Mission"
	_rec_name = 'numero_mission'

	numero_mission = fields.Char("Numero de la mission")
	objet_mission = fields.Text(string = "Objet de la mission", required = True)
	#motifs = fields.Text(string='Motifs',sanitize=False,required=True)
	date_debut = fields.Date("Date de départ" ,default=fields.Date.context_today, required = True)
	date_fin = fields.Date("Date de retour", required = True)
	nombre_nuites = fields.Integer(string = 'Nombre de nuités',compute ='_compute_duree',store=True)
	duree = fields.Integer(string='Durée' ,compute='_compute_duree' ,store=True)
	chef_mission = fields.Many2one("hr.employee",string="Chef de mission", required = True)
	observations = fields.Text(string = 'Observations')
	lieu_depart = fields.Many2one('lieu',string="Lieu de départ", required = True)
	lieu_arrive = fields.Many2one('lieu',string="Lieu d'arrivé", required = True)
	state = fields.Selection([
							 ('open',"Brouillon"),
							 ('in_progress',"En cours"),
							 ('done',"Terminée")
							 ], string="Etat", default='open')
	trajet = fields.Text(string="Trajet",required=True)
	equipe_mission = fields.One2many('missionnaire','mission_id','Equipe de la mission')
	#vehicule_ids = fields.One2many('vehicle_mission' , 'mission_id','Vehicules')
	vehicule_ids = fields.One2many('fleet.vehicle.log.fuel' , 'mission_id','Vehicules')
	#bon_carburant_ids = fields.One2many('fleet.vehicle.log.fuel','mission_id','Bons de carburant' """,compute='_compute_nombre_litres',store=True""")
	#mission_type_id = fields.Many2one('mission.type',string="Type mission")
	type_mission = fields.Selection(TYPE_MISSION,string='Type',default='interieur',required = True)
	#type_mission = fields.Many2one('fongip.mission.type',string='Type de mission')
	#type_mission_name = fields.Char(related="type_mission.name",store=True)
	zone = fields.Many2one('mission.zone',string="Zone", required = True)
	moyen_transport = fields.Selection(MOYEN_TRANSPORT,'Moyen de transport',default='voiture', required = True)
	cout_mission = fields.Float(string='Cout de la mission',digits=(12,0), compute='_compute_cout_mission' , store=True )
	total_perdieme = fields.Float(string='Total perdieme',digits=(12,0),compute='_compute_perdieme',store=True )#,compute='_compute_perdieme',store=True)#""", compute='_compute_perdieme',store=True""")
	total_avance = fields.Float(string='Total avance',digits=(12,0) ,compute='_compute_perdieme',store=True)#, compute='_compute_perdieme',store=True)
	total_restant = fields.Float(string='Total restant',digits=(12,0) ,compute='_compute_perdieme',store=True)#, compute='_compute_perdieme',store=True)
	nombre_de_litres = fields.Float(string='Nombre de litres attribués',compute='_compute_nombre_litres',store=True )#
	distance = fields.Integer(string='Distance en km',default=100)#,compute='_compute_distance',store=True
	dotation_carburant = fields.Float(string='Dotation en carburant' , compute='_compute_dotation_carburant',store=True)
	#prix_au_litre = fields.Float(string='prix au litre (FCFA)' , default=775)
	cout_carburant = fields.Float(string='Cout du carburant' , compute='_compute_cout_carburant' ,store=True)
	carte_carburant = fields.Many2one('carte.carburant',string="Selectionner la carte de carburant")
	source = fields.Selection(SOURCE,'Source',default='carte')
	nombre_tickets = fields.Integer(string="Nombre de tickets")
	#montant_avance_en_lettre = fields.Char(string="Montant avancé en lettres")
	#montant_restant_en_lettre = fields.Char(string="Montant reliquat en lettres")
	lettre_de_mission = fields.Many2many('ir.attachment' ,string="Joindre la lettre de mission signée")
	#rapport_de_mission = fields.Many2many('ir.attachment' ,string="Joindre le rapport de mission")	
	visible = fields.Boolean(default=True)
	perdium_mode_payment_id = fields.Many2one('perdium.mode.payment',default=lambda self:self.env['perdium.mode.payment'].search([('type_mission','=','interieur')],limit=1), string = "Mode de paiement du perdiem")

	@api.model
	def create(self,vals):
		vals['numero_mission'] = self.env['ir.sequence'].next_by_code('mission')
		return super(Mission,self).create(vals)
	"""@api.model
	def default_get(self,fields):
		res = super(Mission,self).default_get(fields)
		type_mission = self.env['fongip.mission.type'].search([('name','like','interieur')],limit=1)
		lieu_depart = self.env['fongip.ville'].search([('name','like','Dakar')],limit=1)
		dico = {}
		if 'type_mission' in fields and type_mission:
			dico['type_mission'] = type_mission.id
		if 'lieu_depart' in fields and lieu_depart:
			dico['lieu_depart'] = lieu_depart.id 

		res.update(dico)
		return res"""

	"""@api.model
	def create(self,vals):
		if 'vehicule_ids' in vals and vals['vehicule_ids']:
			if 'source' in vals and not vals['source'] :
				raise UserError(_("Veuillez selectionner la source du carburant : carte ou ticket"))
			if 'source' in vals and  vals['source'] and ('carte_carburant' in vals and not vals['carte_carburant']):
				raise UserError(_("Veuillez selectionner la carte du carburant"))
		vals['numero_mission'] = self.env['ir.sequence'].next_by_code('mission')
		return super(Mission,self).create(vals)"""


	"""@api.multi
	def write(self,vals):
		if 'vehicule_ids' in vals and vals['vehicule_ids']:
			if 'source' in vals and not vals['source'] :
				raise UserError(_("Veuillez selectionner la source du carburant : carte ou ticket"))
			if 'source' in vals and  vals['source'] and ('carte_carburant' in vals and not vals['carte_carburant']):
				raise UserError(_("Veuillez selectionner la carte du carburant"))
		return super(Mission,self).write(vals)"""


	@api.onchange('type_mission')
	def onchange_type_mission(self):
		if self.type_mission:
			perdium = self.env['perdium.mode.payment'].search([('type_mission','=',self.type_mission)],limit=1)
			if perdium:
				self.perdium_mode_payment_id = perdium
				if perdium.mode_payment == 'paiement_partiel':
					self.visible = True
				else:
					self.visible = False


	"""def action_print_etat_liquidatif(self):
		return self.env.ref('missions.report_etat_liquidatif_mission').report_action(self)"""

	"""@api.multi
	def action_print_all_ordre_mission(self):
		for record in self.equipe_mission:
			print record.first_name
			record.action_print_ordre_mission()"""

	@api.depends('date_debut','date_fin')
	def _compute_duree(self):
		for record in self:
			if record.date_fin:
				duree = (fields.Date.from_string(record.date_fin) - fields.Date.from_string(record.date_debut)).days
				record.duree = duree + 1
				record.nombre_nuites = duree 


	@api.depends('equipe_mission.montant_avance','equipe_mission.montant_restant','equipe_mission.montant_total')
	def _compute_perdieme(self):
		for record in self:
			record.total_avance = sum(record.equipe_mission.mapped('montant_avance'))
			record.total_restant = sum(record.equipe_mission.mapped('montant_restant'))
			record.total_perdieme = sum(record.equipe_mission.mapped('montant_total'))
			
	@api.onchange('nombre_nuites','zone')
	def onchange_perdieme(self):
		if self.type_mission and self.nombre_nuites and self.zone and self.equipe_mission:
			for missionnaire in self.equipe_mission:
				if missionnaire.rang_hierarchique_id:
					indemnite = self.env['mission.indemnite.journaliere'].search([('zone','=',self.zone.id),('rang_hierarchique_id','=',missionnaire.rang_hierarchique_id.id)],limit=1)
					if indemnite:
						missionnaire.indemnite_journaliere = indemnite.montant
						if self.perdium_mode_payment_id:
							if self.perdium_mode_payment_id.mode_payment == 'paiement_partiel':
								if self.perdium_mode_payment_id.pourcentage.__contains__('/'):
									liste = self.perdium_mode_payment_id.pourcentage.split('/')
									numerateur,denominateur = int(liste[0]),int(liste[1])
									missionnaire.montant_avance = round((self.nombre_nuites * indemnite.montant * numerateur) / denominateur)
									missionnaire.montant_restant = self.nombre_nuites * indemnite.montant - missionnaire.montant_avance
							else:
								missionnaire.montant_avance = self.nombre_nuites * indemnite.montant
								missionnaire.montant_restant = 0

	def commencer(self):
		for record in self:
			if record.vehicule_ids and record.equipe_mission:
				record.state = 'in_progress'
				"""for vehicle in record.vehicule_ids:
					vehicle.vehicle_id.write({'status' :'en_mission'})
				for employe in record.equipe_mission:
					employe.employee_id.write({'status':'en_mission'})"""
				
			else:
				#UserError(_("Veuillez renseigner les misionnaires et les vehicules "))
				return False
		return True
			

	def terminer(self):
		for record in self:
			record.state = 'done'
			"""for vehicle in record.vehicule_ids:
				vehicle.vehicle_id.write({'status':'disponible'})
			for employe in record.equipe_mission:
				employe.employee_id.write({'status':'disponible'})"""

		return True

			
	def annuler(self):
		for record in self:
			record.state='open'
			"""for vehicle in record.vehicule_ids:
				vehicle.vehicle_id.write({'status':'disponible'})
			for employe in record.equipe_mission:
				employe.employee_id.write({'status':'disponible'})"""
			

	@api.depends('cout_carburant','total_perdieme')
	def _compute_cout_mission(self):
		self.cout_mission = self.cout_carburant + self.total_perdieme
		"""for record in self:
			if record.cout_carburant and not record.total_perdieme:
				self.cout_mission = record.cout_carburant
			elif record.total_perdieme and not record.cout_carburant:
				self.cout_mission = record.total_perdieme
			else:
				self.cout_mission = record.cout_carburant + record.total_perdieme"""

	"""@api.onchange('cout_carburant','total_perdieme')
	def onchange_cout_mission(self):
		if self.cout_carburant and not self.total_perdieme:
			self.cout_mission = self.cout_carburant
		elif self.total_perdieme and not self.cout_carburant:
			self.cout_mission = self.total_perdieme
		else:
			self.cout_mission = self.cout_carburant + self.total_perdieme"""



	@api.depends('distance')
	def _compute_nombre_litres(self):
		nombre_de_litres = 15 * self.distance /100
		nombre_de_litres = nombre_de_litres if (15 * self.distance) % 100 == 0 else nombre_de_litres + 1
		self.nombre_de_litres = nombre_de_litres

	@api.onchange('nombre_de_litres')
	def onchange_nombre_litres(self):
		if self.vehicule_ids:
			for vehicle in self.vehicule_ids:
				vehicle.liter = self.nombre_de_litres


	"""@api.depends('lieu_depart','lieu_arrive')
	def _compute_distance(self):
		if self.lieu_depart and self.lieu_arrive:
			self.distance = (self.lieu_arrive.distance - self.lieu_depart.distance) * 2 # on calcule distance aller - retour

	@api.onchange('distance','vehicule_ids','prix_au_litre')
	def onchange_distance(self):
		bon_carburant = []
		carte_carburant = False
		if self.distance and not self.vehicule_ids:
			nombre_de_litres = 15 * self.distance /100
			nombre_de_litres = nombre_de_litres if (15 * self.distance) % 100 == 0 else nombre_de_litres + 1
			self.nombre_de_litres = nombre_de_litres
		if self.distance and self.vehicule_ids and self.prix_au_litre:
			if self.carte_carburant:
					carte_carburant = self.carte_carburant.id
			nombre_de_litres = 15 * self.distance /100
			nombre_de_litres = nombre_de_litres if (15 * self.distance) % 100 == 0 else nombre_de_litres + 1
			self.nombre_de_litres = nombre_de_litres
			for vehicle in self.vehicule_ids:
				liter = nombre_de_litres#(15 * self.distance) / 100
				price_per_liter = self.prix_au_litre
				amount = liter * price_per_liter
				bon_carburant.append((0,0,{'vehicle_id':vehicle.vehicle_id,'liter':liter,'price_per_liter':price_per_liter,'amount':amount,'carte_carburant':carte_carburant,'nombre_tickets':self.nombre_tickets,'source':self.source,'destination':self.lieu_arrive.name,'conducteur':vehicle.conducteur.id}))#
				#if self.source == 'ticket':
				#bon_carburant.append((0,0,{'vehicle_id':vehicle.vehicle_id,'liter':liter,'price_per_liter':price_per_liter,'amount':amount,'nombre_tickets':self.nombre_tickets,'source':self.source,'destination':self.lieu_arrive}))
			
			self.bon_carburant_ids = bon_carburant"""

	"""@api.onchange('chef_mission')
	def onchange_chef_mission(self):
		if self.chef_mission and not self.equipe_mission:
			#ajout sur les missionnaires
			missionnaires = []
			liste = self.chef_mission.name.split(' ')
			last_name = liste[-1]
			first_name = " ".join(liste[:-1])
			montant_avance = 0
			montant_restant = 0
			dico = {'employee_id':self.chef_mission.id,'first_name':first_name,'last_name':last_name,'numero_ordre':0,'prise_en_charge':'perdieme'}
			#type_missionnaire
			type_missionnaire = self.env['type.missionnaire'].search([('name','like','AGENT')],limit=1)
			if type_missionnaire:
				dico['type_missionnaire'] = type_missionnaire.id
			if self.type_mission_name == 'interieur':
				dico['indemnite_journaliere'] = self.type_mission.montant
				dico['montant_avance'] = self.nombre_nuites * round((2 * self.type_mission.montant) / 3.0)
				dico['montant_restant'] = self.nombre_nuites * (self.type_mission.montant - round((2 * self.type_mission.montant) / 3.0))
			if self.type_mission_name == 'exterieur':
				indemnite = self.env['mission.indemnite.journaliere'].search([('type_mission','=',self.type_mission.id),('zone','=',self.zone.id),('type_missionnaire','=',type_missionnaire.id)],limit=1)
				if indemnite:
					dico['indemnite_journaliere'] = indemnite.montant
					dico['montant_avance'] = self.nombre_nuites * round((4 * indemnite.montant) / 5.0)
					dico['montant_restant'] = self.nombre_nuites * (indemnite.montant - round((4 * indemnite.montant) / 5.0))

			missionnaires.append((0,0,dico))
			self.equipe_mission = missionnaires"""



	@api.depends('vehicule_ids.liter')
	def _compute_dotation_carburant(self):
		self.dotation_carburant = sum(self.vehicule_ids.mapped('liter'))

	"""@api.onchange('carte_carburant')
	def onchange_carte_carburant(self):
		if self.carte_carburant:
			if self.carte_carburant.quantite_actuelle < self.dotation_carburant:
				raise UserError(_("Le nombre de litres restant dans la carte est insuffisant , merci de recharger la carte."))
			if self.bon_carburant_ids:
				for line in self.bon_carburant_ids:
					line.update({'carte_carburant':self.carte_carburant.id,'source':'carte'})"""

	@api.onchange('source')
	def onchange_source(self):
		if self.source=='ticket':
			self.carte_carburant = False
			self.nombre_tickets = self.dotation_carburant / 10 if (self.dotation_carburant % 10) == 0 else self.dotation_carburant / 10 +1
			for line in self.vehicule_ids:#self.bon_carburant_ids:
				line.update({'carte_carburant':False,'source':'ticket','nombre_tickets':self.nombre_tickets})
		if self.source == 'carte':
			for line in self.vehicule_ids:#self.bon_carburant_ids:
				line.update({'nombre_tickets':0,'source':'carte'})



	#@api.depends('dotation_carburant','prix_au_litre')
	#@api.depends('bon_carburant_ids.amount')
	@api.depends('vehicule_ids.amount')
	def _compute_cout_carburant(self):
		#self.cout_carburant = sum(self.bon_carburant_ids.mapped('amount'))
		self.cout_carburant = sum(self.vehicule_ids.mapped('amount'))
	

	#cron pour demarrer ou terminer une mission
	"""def demarrer_ou_terminer_mission(self):
		date_today = fields.Date.from_string(fields.Date.context_today(self))
		date_debut = fields.Date.from_string(self.date_debut)
		date_fin = fields.Date.from_string(self.date_fin)
		#informer à RH les employes en mission
		#Find the mail template
		template = self.env.ref('fongip_parc_automobile.email_template_info_mission_for_rh')
		
		if date_debut == date_today:
			if self.commencer():
				#send out the e-mail template to the user
				self.env['mail.template'].browse(template.id).send_mail(self.id)
		if date_fin == date_today:
			if self.terminer():
				#send out the e-mail template to the user
				self.env['mail.template'].browse(template.id).send_mail(self.id)
		return True"""

	#@api.model 
	"""def run_scheduler(self):
		self.demarrer_ou_terminer_mission()"""

	

"""class FongipDemandeService(models.Model):
	_name = 'demande.service'
	_description = "Demande de service sur les vehicules"
	_rec_name = 'numero_demande'
	numero_demande = fields.Char(string="Numéro demande ")
	employee_id = fields.Many2one('hr.employee',string='Employé' , readonly=True)
	service_demandeur = fields.Many2one('hr.department',string = 'Service demandeur')
	date_demande = fields.Date(string='Date de la demande' , default=fields.Date.context_today)
	vehicle_id = fields.Many2one('fleet.vehicle',string='Véhicule concerné')
	objet_demande = fields.Text(string='Objet de la demande')
	state = fields.Selection([('draft',"Brouillon"),('confirm',"Confimé"),('visa_rmg',"Visa RMG")],string="Etat",default='draft') #,('validation_daf',"Validation DAF")



	@api.multi
	def confirmer(self):
		for record in self:
			record.state = 'confirm'
			
	@api.multi
	def visa_rmg(self):
		for record in self:
			record.state = 'visa_rmg'

	@api.multi
	def validation_daf(self):
		for record in self:
			record.state = 'validation_daf'




	@api.model
	def default_get(self,fields):
		res = super(FongipDemandeService,self).default_get(fields)
		employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
		data = {}
		if 'employee_id' in fields and employee :
			data['employee_id'] = employee.id
			if employee.department_id:
				data['service_demandeur'] = employee.department_id.id
			res.update(data)

		return res

	@api.model 
	def create(self,vals):
		vals['numero_demande'] = self.env['ir.sequence'].next_by_code('demande.service')
		return super(FongipDemandeService,self).create(vals)
"""



"""class CarteCarburant(models.Model):
	_name = 'fongip.carte.carburant'
	_description = 'Model de carte de carburant'
	_order = 'numero_carte asc'

	name = fields.Char(string="Libellé")
	numero_carte = fields.Char(string="Numéro carte",required=True)
	detenteur = fields.Many2one('hr.employee',string="Détenteur de la carte ")
	fournisseur = fields.Many2one('res.partner',string="Fournisseur",domain="[('supplier','=',True)]")
	chargement_carte_ids = fields.One2many('fongip.chargement.carte','carte_carburant',string="Chargements")
	quantite = fields.Integer(string="Quantité Totale",compute="_compute_total",store=True)
	bon_carburant_ids = fields.One2many('fleet.vehicle.log.fuel','carte_carburant','Bons de carburant')
	consommation = fields.Integer(string="Nombre de litres consommés",compute="_compute_consommation",store=True)
	quantite_actuelle = fields.Integer(string="Quantité actuelle", compute="_compute_quantite_actuelle",store=True)#,compute="_compute_quantite",store=True
	montant_consommation = fields.Float(string="Montant consommation",digits=(12,0),compute="_compute_consommation",store=True)
	montant = fields.Float(string="Montant",digits=(12,0),compute="_compute_total",store=True)
	color = fields.Integer(string = 'Color Index', default = 0)
	type_carte = fields.Selection(TYPE_CARTE_CARBURANT,'Type de carte',default='personnel')

	_sql_constraints = [('numero_carte_unique', 'unique (numero_carte)', "Ce numéro de carte existe déja, merci de choisir un autre numéro de carte")]
	
	@api.depends('chargement_carte_ids')
	def _compute_total(self):
		if self.chargement_carte_ids:
			self.quantite = sum(self.chargement_carte_ids.mapped('quantite'))
			self.montant = sum(self.chargement_carte_ids.mapped('montant'))
			#self.montant_consommation = sum(self.chargement_carte_ids.mapped())

	@api.depends('quantite','consommation')
	def _compute_quantite_actuelle(self):
		if self.quantite and not self.consommation:
			self.quantite_actuelle = self.quantite
		elif self.quantite and self.consommation:
			self.quantite_actuelle = self.quantite - self.consommation
		


	@api.depends('bon_carburant_ids')
	def _compute_consommation(self):
		if self.bon_carburant_ids:
			self.consommation = sum(self.bon_carburant_ids.mapped('liter'))
			self.montant_consommation = sum(self.bon_carburant_ids.mapped('cost_amount'))



class ChargementCarte(models.Model):
	_name = 'fongip.chargement.carte'
	_rec_name = 'carte_carburant'
	carte_carburant = fields.Many2one('fongip.carte.carburant',string="Carte",ondelete="cascade")
	date = fields.Date(string="Date ")
	quantite = fields.Integer(string="Nombre de litres")
	prix_unitaire = fields.Float(string="Prix au litre",digits=(4,0),default=775)
	montant = fields.Float(string="Montant",digits=(12,0),compute="_compute_montant",store=True)


	@api.depends('quantite','prix_unitaire')
	def _compute_montant(self):
		for record in self:
			if record.quantite and record.prix_unitaire:
				record.montant = record.quantite * record.prix_unitaire




class CarnetDeBord(models.Model):
	_name = 'fongip.carnet_de_bord'
	_description = 'Carnet de bord de vehicule'
	
	vehicule = fields.Many2one('fleet.vehicle',string="Véhicule" , ondelete='cascade')
	source = fields.Selection(SOURCE,'Source',default='ticket')
	nombre_tickets = fields.Integer(string="Nombre de tickets")
	carte_carburant = fields.Many2one('fongip.carte.carburant',string='carte_carburant')
	date_heure = fields.Datetime(string="Date et heure")
	date = fields.Date(string="Date",compute='_compute_date_heure',store=True)
	heure = fields.Char(string="Heure de départ",compute='_compute_date_heure',store=True)
	conducteur = fields.Many2one('hr.employee' ,string="Conducteur")
	destination = fields.Char(string="Destination")
	kilometrage = fields.Float(string="Kilométrage")
	carburant = fields.Float(string="Attribution de carburant (en litre)")
	observations = fields.Text(string="Observations")

	@api.one
	@api.depends('date_heure')
	def _compute_date_heure(self):
		if self.date_heure:
			self.date, self.heure = self.date_heure.split(' ')[0], self.date_heure.split(' ')[1]"""



class FongipVille(models.Model):
	_name = 'lieu'
	_description = 'lieu'
	name = fields.Char(string="Nom du lieu")
	#distance = fields.Integer(string='Distance par rapport à Dakar')
	_sql_constraints = [('name_unique', 'unique (name)', "Ce nom de ville existe déjà, merci de choisir un autre nom de ville")]


#Entretien et reparation

