from application.extensions import db
from functools import total_ordering
from datetime import datetime

from application.data import final_states

class OrderedMixin:

    def __eq__(self, other):
        return self.start_date == other.start_date

    def __lt__(self, other):
        return self.start_date < other.start_date


@total_ordering
class CompulsoryPurchaseOrder(db.Model, OrderedMixin):

    compulsory_purchase_order = db.Column(db.String(), primary_key=True, nullable=False)
    name = db.Column(db.String())
    organisation = db.Column(db.String())
    compulsory_purchase_order_type = db.Column(db.String())
    description = db.Column(db.String())
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())

    legislation = db.Column(db.String())
    legislation_name = db.Column(db.String())
    legislation_url = db.Column(db.String())

    investigations = db.relationship('CompulsoryPurchaseOrderInvestigation',
                                     lazy='joined',
                                     back_populates='compulsory_purchase_order',
                                     order_by='CompulsoryPurchaseOrderInvestigation.start_date')

    statuses = db.relationship('CompulsoryPurchaseOrderStatus',
                               lazy='joined',
                               back_populates='compulsory_purchase_order',
                               order_by='CompulsoryPurchaseOrderStatus.start_date')

    def latest_status(self):
        return self.statuses[-1]

    def latest_investigation_status(self):
        if self.has_inquiry():
            return self.investigations[-1]
        else:
            return None

    def has_final_status(self):
        if self.has_inquiry():
            return self.latest_investigation_status().is_final_state()
        else:
            return self.latest_status().is_final_state()

    def days_to_completion(self):
        if not self.has_final_status():
            return None
        start_date = self.statuses[0].start_date

        if self.has_inquiry():
            end_date = self.latest_investigation_status().start_date
        else:
            end_date = self.latest_status().start_date

        return abs((start_date - end_date).days)

    def days_for_inquiry(self):
        try:
            if not self.has_final_status() or not self.has_inquiry():
                return None
            start_date = self.investigations[0].start_date
            end_date = self.latest_investigation_status().start_date

            return abs((start_date - end_date).days)
        except Exception as e:
            print(e)
            return 0

    def days_since_received(self):
        today = datetime.now().date()
        start_date = self.statuses[0].start_date
        return abs((start_date - today).days)

    def has_inquiry(self):
        return len(self.investigations) > 0


@total_ordering
class CompulsoryPurchaseOrderInvestigation(db.Model, OrderedMixin):

    compulsory_purchase_order_investigation = db.Column(db.Integer(), primary_key=True, nullable=False)
    status = db.Column(db.String())
    inspector_report_url = db.Column(db.String())
    decision_url = db.Column(db.String())
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())

    compulsory_purchase_order_id = db.Column(db.String, db.ForeignKey('compulsory_purchase_order.compulsory_purchase_order'))
    compulsory_purchase_order = db.relationship('CompulsoryPurchaseOrder',  back_populates='investigations')

    def is_final_state(self):
        return self.status in final_states


@total_ordering
class CompulsoryPurchaseOrderStatus(db.Model, OrderedMixin):

    compulsory_purchase_order_status = db.Column(db.Integer(), primary_key=True, nullable=False)
    status = db.Column(db.String())
    document_url = db.Column(db.String())
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())

    compulsory_purchase_order_id = db.Column(db.String, db.ForeignKey('compulsory_purchase_order.compulsory_purchase_order'))
    compulsory_purchase_order = db.relationship('CompulsoryPurchaseOrder', back_populates='statuses')

    def is_final_state(self):
        return self.status in final_states