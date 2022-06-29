# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

SOURCE = [
				('carte','Carte'),
				('ticket','Ticket'),
		 ]

class Carburant(models.Model):
	_name = 'fleet.vehicle.log.fuel'
	_inherit = 'fleet.vehicle.log.fuel'
	price_per_liter = fields.Float(default=775)
	mission_id = fields.Many2one('mission',string='Mission',ondelete='cascade')
	carte_carburant = fields.Many2one('carte.carburant',string="Selectionner la carte de carburant",ondelete='cascade')
	source = fields.Selection(SOURCE,'Source', required = True)
	nombre_tickets = fields.Integer(string="Nombre de tickets")
	#---------rrrrrrrrrrrrrrrrr------------------------
	#date_heure = fields.Datetime(string="Date et heure")
	#date = fields.Date(string="Date",compute='_compute_date_heure',store=True)
	#heure = fields.Char(string="Heure de départ",compute='_compute_date_heure',store=True)
	conducteur = fields.Many2one('hr.employee' ,string="Conducteur")
	destination = fields.Text(string="Destination")
	#kilometrage = fields.Float(string="Kilométrage")
	#carburant = fields.Float(string="Attribution de carburant (en litre)")
	observations = fields.Text(string="Observations")


	"""def unlink(self):
		for record in self:
			vehicle_mission = self.env['vehicle_mission'].search([('vehicle_id','=',record.vehicle_id.id),('mission_id','=',record.mission_id.id)])
			if vehicle_mission:
				vehicle_mission.unlink()
		return super(Carburant,self).unlink()"""

	@api.onchange('source')
	def onchange_source(self):
		if self.source and self.vehicle_id and self.mission_id:
			self.liter = self.mission_id.nombre_de_litres
			if self.source == "ticket":
				reste = self.mission_id.nombre_de_litres % 10
				if reste == 0:
					self.nombre_tickets = self.mission_id.nombre_de_litres // 10
				else:
					self.nombre_tickets = self.mission_id.nombre_de_litres // 10 + 1	





	@api.onchange('nombre_tickets')
	def onchange_nombre_tickets(self):
		if self.nombre_tickets:
			self.liter = self.nombre_tickets * 10
			self.amount = self.nombre_tickets * 10 * self.price_per_liter
