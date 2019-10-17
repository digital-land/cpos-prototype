from datetime import date, timedelta

from application.models import (CompulsoryPurchaseOrder,
                                CompulsoryPurchaseOrderInvestigation,
                                CompulsoryPurchaseOrderStatus)


def test_compulsory_purchase_orders_can_be_ordered_by_start_date():

    a_week_ago = date.today() - timedelta(days=7)
    yesterday = date.today() - timedelta(days=1)

    day_old_cpo = CompulsoryPurchaseOrder(compulsory_purchase_order='later_cpo', start_date=yesterday)
    week_old_cpo = CompulsoryPurchaseOrder(compulsory_purchase_order='earlier_cpo', start_date=a_week_ago)

    assert week_old_cpo < day_old_cpo
    assert not week_old_cpo > day_old_cpo


def test_compulsory_purchase_orders_investigations_can_be_ordered_by_start_date():

    a_week_ago = date.today() - timedelta(days=7)
    yesterday = date.today() - timedelta(days=1)

    day_old_investigation = CompulsoryPurchaseOrderInvestigation(compulsory_purchase_order_investigation='later_investigation', start_date=yesterday)
    week_old_investigation = CompulsoryPurchaseOrderInvestigation(compulsory_purchase_order_investigation='earlier_investigation', start_date=a_week_ago)

    assert week_old_investigation < day_old_investigation
    assert not week_old_investigation > day_old_investigation
    assert week_old_investigation != day_old_investigation


def test_compulsory_purchase_orders_statuses_can_be_ordered_by_start_date():

    a_week_ago = date.today() - timedelta(days=7)
    yesterday = date.today() - timedelta(days=1)

    day_old_status = CompulsoryPurchaseOrderStatus(compulsory_purchase_order_status='later_status', start_date=yesterday)
    week_old_status = CompulsoryPurchaseOrderStatus(compulsory_purchase_order_status='earlier_status', start_date=a_week_ago)

    assert week_old_status < day_old_status
    assert not week_old_status > day_old_status
    assert week_old_status != day_old_status


def test_cpo_equals():

    cpo = CompulsoryPurchaseOrder(compulsory_purchase_order='some_cpo')
    same_cpo_id = CompulsoryPurchaseOrder(compulsory_purchase_order='some_cpo')
    some_other_cpo = CompulsoryPurchaseOrder(compulsory_purchase_order='some_other_cpo')

    assert cpo == same_cpo_id
    assert cpo != some_other_cpo


def test_cpo_investigation_equals():

    cpo_investigation = CompulsoryPurchaseOrderInvestigation(compulsory_purchase_order_investigation='some_cpo_investigation')
    same_cpo_investigation_id = CompulsoryPurchaseOrderInvestigation(compulsory_purchase_order_investigation='some_cpo_investigation')
    some_other_cpo_investigation = CompulsoryPurchaseOrderInvestigation(compulsory_purchase_order_investigation='some_other_cpo_investigation')

    assert cpo_investigation == same_cpo_investigation_id
    assert cpo_investigation != some_other_cpo_investigation


def test_cpo_status_equals():

    cpo_status = CompulsoryPurchaseOrderStatus(compulsory_purchase_order_status='some_cpo_status')
    same_cpo_status_id = CompulsoryPurchaseOrderStatus(compulsory_purchase_order_status='some_cpo_status')
    some_other_cpo_status = CompulsoryPurchaseOrderStatus(compulsory_purchase_order_status='some_other_cpo_status')

    assert cpo_status == same_cpo_status_id
    assert cpo_status != some_other_cpo_status

