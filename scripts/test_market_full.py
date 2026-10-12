import sys
import os

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pipeline", "src"))
from gem_pipeline.market.role_profiler import RoleSkillProfiler

def main():
    profiler = RoleSkillProfiler()
    summary = profiler.get_all_role_summaries()
    roles = summary.get('roles', [])
    print(f"Total Roles in Taxonomy: {len(roles)}")
    print(f"Total JDs in Corpus: {summary.get('total_jds_in_corpus')}")
    print("\nTop 10 Roles by Demand in TopCV Corpus:")
    for i, r in enumerate(roles[:10], 1):
        print(f"  {i}. {r['specific_role']} ({r['domain']}): {r['jd_count']} JDs ({r['share_pct']:.2f}%)")

    print("\n" + "=" * 60)
    for role_name in ['AI Engineer', 'Backend Developer', 'Data Engineer', 'Automation Tester']:
        prof = profiler.get_role_skill_profile(role_name)
        print(f"\n🎯 [ROLE PROFILE] {role_name} (Total JDs: {prof.get('total_jds', 0)}):")
        core = [f"{s['canonical_name']} ({s['demand_pct']:.1f}%)" for s in prof.get('core_skills', [])[:5]]
        boosters = [f"{s['canonical_name']} ({s['demand_pct']:.1f}%)" for s in prof.get('boost_skills', [])[:5]]
        print(f"   - Core Must-Haves: {', '.join(core) if core else 'N/A'}")
        print(f"   - Career Boosters: {', '.join(boosters) if boosters else 'N/A'}")

if __name__ == '__main__':
    main()
