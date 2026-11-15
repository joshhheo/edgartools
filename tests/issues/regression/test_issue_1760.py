"""Regression coverage for whitespace in set-valued XBRL facts.

GitHub Issue: https://github.com/dgunning/edgartools/issues/1760
"""

from edgar.xbrl import XBRL

CONCEPT = (
    "EffectiveIncomeTaxRateReconciliationStateAndLocalJurisdiction"
    "ContributionGreaterThan50PercentTaxEffectExtensibleEnumeration"
)


def test_enumeration_duplicates_preserve_the_first_filed_value():
    # Cracker Barrel FY2026 10-K, accession 0001104659-26-110772, Note 14.
    # Use the reported jurisdictions in a minimal instance with synthetic duplicates.
    members = [f"http://xbrl.sec.gov/stpr/2026#{state}" for state in ("IL", "KY", "TN", "TX")]
    filed_value = "\n".join(members)
    spaced_value = " ".join(members)
    distinct_value = " ".join(members[:-1])
    xbrl = XBRL()
    xbrl.parser.parse_instance_content(f"""
    <xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
                xmlns:us-gaap="http://fasb.org/us-gaap/2026">
      <xbrli:context id="c">
        <xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">1067294</xbrli:identifier></xbrli:entity>
        <xbrli:period><xbrli:startDate>2025-08-02</xbrli:startDate><xbrli:endDate>2026-07-31</xbrli:endDate></xbrli:period>
      </xbrli:context>
      <us-gaap:{CONCEPT} id="f1" contextRef="c">{filed_value}</us-gaap:{CONCEPT}>
      <us-gaap:{CONCEPT} id="f2" contextRef="c">{spaced_value}</us-gaap:{CONCEPT}>
      <us-gaap:{CONCEPT} id="f3" contextRef="c">{distinct_value}</us-gaap:{CONCEPT}>
    </xbrli:xbrl>
    """)

    assert xbrl.facts.to_dataframe()["value"].tolist() == [filed_value, distinct_value]
    query = xbrl.facts.query().by_concept(CONCEPT)
    assert query.to_dataframe("value")["value"].tolist() == [filed_value, distinct_value]
