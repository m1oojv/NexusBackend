import csv
import os
import json

from sqlalchemy import null
from db.models import Actor, AssetCostFraud, AssetCostRecord, AssetDdosCost, AssetDowntimeIndustry, ThreatScenario, TefCompanySize, TefIndustry,\
                    BusinessImpact, ControlAttribute, ControlSmeEstimated, Industry, MitreAttackTechniqueControlAttribute, MitreAttackTechnique,\
                    ThreatScenarioMitreAttackTechnique, ThreatScenarioControlAttribute, ThreatScenario, Vector, Company, CompanyThreatScenario,\
                    ControlAssessment, ControlFamilyAssessmentProgress, Financial, Score, ScoreResult

from db.database import session

def seed_actor():
  try:    
    with open(os.path.join('db', 'actor.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = Actor(**{
          'id': row[2],
          'threat_scenario_id': row[0],
          'name': row[1]          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_asset_cost_fraud():  
  try:    
    with open(os.path.join('db', 'asset_cost_fraud.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = AssetCostFraud(**{
          'id': row[0],
          'company_size': row[1],
          'cost': row[2],
          'cost_item': row[3],          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_asset_cost_fraud():  
  try:    
    with open(os.path.join('db', 'asset_cost_fraud.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = AssetCostFraud(**{
          'id': row[0],
          'company_size': row[1],
          'cost': row[2],
          'cost_item': row[3],          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_asset_cost_record():  
  try:    
    with open(os.path.join('db', 'asset_cost_record.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = AssetCostRecord(**{
          'id': row[1],
          'records_category': row[2],
          'cost_low': row[3],
          'cost_mode': row[4],
          'cost_high': row[5],
          'cost_item': row[6],          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_asset_ddos_cost():  
  try:    
    with open(os.path.join('db', 'asset_ddos_cost.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = AssetDdosCost(**{
          'id': row[1],
          'company_size': row[2],
          'cost': int(float(row[3]))
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_asset_downtime_industry():  
  try:    
    with open(os.path.join('db', 'asset_downtime_industry.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = AssetDowntimeIndustry(**{
          'id': row[1],
          'industry': row[2],
          'threat_category': row[3],
          'impact': row[4],
          'ratio': row[5],
          'downtime_low': row[6],
          'downtime_mode': row[7],
          'downtime_high': row[8],
        })        
        session.add(record)    
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_business_impact():
  try:    
    with open(os.path.join('db', 'business_impact.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = BusinessImpact(**{
          'id': row[2],
          'name': row[1],
          'threat_scenario_id': row[0]          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_company_threat_scenario():
  try:    
    with open(os.path.join('db', 'company_threat_scenario.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = CompanyThreatScenario(**{
          'id': row[0],
          'company_id': row[1],
          'threat_scenario_id': row[2]          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_company():
  try:
    f = open(os.path.join('db', 'envipure.json'))
    data = json.load(f)
    
    with open(os.path.join('db', 'company.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      last_assessed_at = null()
      application_datetime = null()
      tenant_id = null()

      for row in rows:        
        print(row)
        if row[7] == '':          
          last_assessed_at = null()          
        else:
          last_assessed_at = row[7]

        if row[18] == '':
          application_datetime = null()
        else:
          application_datetime = row[18]

        if row[19] == '':
          tenant_id = null()
        else:
          tenant_id = row[19]
        
        record = Company(**{
          'id': row[0],
          'name': row[1],
          'revenue': row[2],
          'industry': row[3],
          'country': row[4],
          'description': row[5],
          'assessment_progress': row[6],
          'last_assessed_at': last_assessed_at,
          'employees': row[8],
          'domain': row[9],
          'threat_assessment_status': row[10],
          'scan_status': row[11],
          'pii': row[12],
          'pci': row[13],
          'phi': row[14],
          'control_status': row[15],
          'scan_results': data,
          'estimated_controls': row[17],
          'application_datetime': application_datetime,
          'tenant_id': tenant_id,
          'user_id': row[20],
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_control_assessment():
  try:    
    with open(os.path.join('db', 'control_assessment.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      completed_datetime = null()
      last_saved = null()
      
      for row in rows:
        print(row)

        if row[3] == '':
          completed_datetime = null()
        else:
          completed_datetime = row[3]

        if row[4] == '':
          last_saved = null()
        else:
          last_saved = row[3]

        record = ControlAssessment(**{
          'id': row[0],
          'company_id': row[1],
          'start_date': row[2],
          'completed_datetime': completed_datetime,
          'last_saved': last_saved
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_control_attribute():
  try:    
    with open(os.path.join('db', 'control_attribute.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      include_sme_assessment = False
      
      for row in rows:
        print(row)
        
        if row[15] == 'FALSE':
          include_sme_assessment == False
        else:
          include_sme_assessment == True

        record = ControlAttribute(**{
          'id': row[0],
          'control_id': row[1],
          'nist_function': row[2],
          'org_control_family': row[3],
          'description': row[4],
          'org_statement_type': row[5],
          'org_control_domain': row[6],
          'enterprise_bu': row[7],
          'maturity': row[8],
          'effectiveness_relevance': row[9],
          'effectiveness_timeliness': row[10],
          'effectiveness_adaptability': row[11],
          'coverage': row[12],
          'source_framework_code': row[13],
          'source_framework': row[14],
          'include_sme_assessment': include_sme_assessment
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_control_assessment():
  try:    
    with open(os.path.join('db', 'control_assessment.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      completed_datetime = null()
      last_saved = null()
      
      for row in rows:
        print(row)

        if row[3] == '':
          completed_datetime = null()
        else:
          completed_datetime = row[3]

        if row[4] == '':
          last_saved = null()
        else:
          last_saved = row[3]

        record = ControlAssessment(**{
          'id': row[0],
          'company_id': row[1],
          'start_date': row[2],
          'completed_datetime': completed_datetime,
          'last_saved': last_saved,
          'control_family_progress': row[5]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_control_family_assessment_progress():
  try:    
    with open(os.path.join('db', 'control_family_assessment_progress.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      last_saved = null()
      
      for row in rows:
        print(row)

        if row[4] == '':
          last_saved = null()
        else:
          last_saved = row[4]                

        record = ControlFamilyAssessmentProgress(**{
          'id': row[0],
          'control_assessment_id': row[1],
          'control_family': row[2],
          'assessment_progress': row[3],
          'last_saved': last_saved          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_control_sme_estimated():
  try:    
    with open(os.path.join('db', 'controls_sme_estimated.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = ControlSmeEstimated(**{
          'id': row[3],
          'company_type': row[0],
          'scan_indicator': row[1],
          'control_attribute_id': row[2]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_financial():
  try:    
    with open(os.path.join('db', 'financial.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      premium = null()
      limits = null()
      claims = null()      

      for row in rows:
        print(row)

        if row[3] == '':
          premium = null()
        else:
          premium = row[3]

        if row[4] == '':
          limits = null()
        else:
          limits = row[4]

        if row[7] == '':
          claims = null()
        else:
          claims = row[7]

        record = Financial(**{
          'id': row[0],
          'company_id': row[1],
          'risk': row[2],
          'premium': premium,
          'limits': limits,
          'loss_exceedence': json.loads(row[5]),
          'threat_category_losses': json.loads(row[6]),
          'claims': claims,
          'loss_by_return_period': json.loads(row[8])
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_industry():
  try:    
    with open(os.path.join('db', 'industry.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = Industry(**{
          'id': row[2],
          'name': row[1],
          'threat_scenario_id': row[0]          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_mitre_attack_technique():
  try:    
    with open(os.path.join('db', 'mitre_attack_technique.csv'), newline='', encoding="utf-8") as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      is_sub_technique = False
      
      for row in rows:
        if row[9] == 'FALSE':
          is_sub_technique = False
        else:
          is_sub_technique = True

        print(row)
        record = MitreAttackTechnique(**{
          'id': row[0],
          'name': row[1],
          'technique_id': row[2],
          'url': row[3],
          'platforms': row[4],
          'tactics': row[5],
          'description': row[6],
          'data_sources': row[7],
          'detection': row[8],
          'is_sub_technique': is_sub_technique,
          'created_at': row[10],
          'updated_at': row[11]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_score_result():
  try:    
    with open(os.path.join('db', 'score_result.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header     

      for row in rows:
        print(row)      

        record = ScoreResult(**{
          'id': row[0],
          'company_id': row[1],
          'control_attribute_id': row[2],
          'existence': row[3],
          'maturity': row[4],
          'effectiveness_relevance': row[5],
          'effectiveness_timeliness': row[6],
          'effectiveness_adaptability': row[7],
          'effectiveness_score': row[8],
          'group_coverage': row[9],
          'tri_score': row[10],
          'tri_score_stage': row[11],
          'nist_function': row[12],
          'threat_scenario_id': row[13],
          'control_assessment_id': row[14]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_score():
  try:    
    with open(os.path.join('db', 'score.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header     

      for row in rows:
        print(row)      

        record = Score(**{
          'id': row[0],
          'company_id': row[1],
          'control_attribute_id': row[2],
          'existence': row[3],
          'maturity': row[4],
          'effectiveness_relevance': row[5],
          'effectiveness_timeliness': row[6],
          'effectiveness_adaptability': row[7],
          'group_coverage': row[8],
          'control_assessment_id': row[9]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_mitre_attack_technique_control_attribute():
  try:    
    with open(os.path.join('db', 'mitre_attack_technique_control_attribute.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = MitreAttackTechniqueControlAttribute(**{
          'id': row[2],
          'mitre_attack_technique_id': row[0],
          'control_attribute_id': row[1]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_tef_company_size():  
  try:    
    with open(os.path.join('db', 'tef_company_size.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = TefCompanySize(**{
          'id': row[6],
          'threat_category': row[1],
          'company_size': row[2],
          'tef_low': row[3],
          'tef_mode': row[4],
          'tef_high': row[5]
        })        
        session.add(record)    
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_tef_industry():  
  try:    
    with open(os.path.join('db', 'tef_industry.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = TefIndustry(**{
          'id': row[1],
          'industry': row[2],
          'threat_category': row[3],
          'risk': row[4],
          'ratio': row[5]          
        })        
        session.add(record)    
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_threat_scenario_control_attribute():
  try:    
    with open(os.path.join('db', 'threat_scenario_control_attribute.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = ThreatScenarioControlAttribute(**{
          'id': row[3],
          'threat_scenario_id': row[0],
          'control_attribute_id': row[2]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_threat_scenario_mitre_attack_technique():
  try:    
    with open(os.path.join('db', 'threat_scenario_mitre_attack_technique.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = ThreatScenarioMitreAttackTechnique(**{
          'id': row[3],
          'threat_scenario_id': row[0],
          'killchain_stage': row[1],
          'mitre_attack_technique_id': row[2],
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_threat_scenario():  
  try:    
    with open(os.path.join('db', 'threat_scenario.csv'), newline='', encoding="utf-8") as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = ThreatScenario(**{
          'id': row[0],
          'title': row[1],
          'description': row[2]
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_vector():
  try:    
    with open(os.path.join('db', 'vector.csv'), newline='') as csvfile:
      rows = csv.reader(csvfile, delimiter=',')
      next(rows) # remove header
      
      for row in rows:        
        print(row)
        record = Vector(**{
          'id': row[0],
          'name': row[2],
          'threat_scenario_id': row[1]          
        })        
        session.add(record)
        
    session.commit() 
  except Exception as e:
    print(e)
    session.rollback()

def seed_data():
  seed_company()
  seed_control_assessment()
  seed_threat_scenario()
  seed_mitre_attack_technique()
  seed_control_attribute()
  seed_actor()
  seed_asset_cost_fraud()
  seed_asset_cost_record()
  seed_asset_ddos_cost()
  seed_asset_downtime_industry()
  seed_business_impact()  
  seed_company_threat_scenario()
  seed_control_family_assessment_progress()
  seed_control_sme_estimated()
  seed_financial()
  seed_industry()  
  seed_mitre_attack_technique_control_attribute()
  seed_score_result()
  seed_score()
  seed_tef_company_size()
  seed_tef_industry()
  seed_threat_scenario_control_attribute()
  seed_threat_scenario_mitre_attack_technique()
  seed_vector()

# Uncomment for local machine usage
seed_data()