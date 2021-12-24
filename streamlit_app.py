from collections import defaultdict
from itertools import combinations, product
from random import sample

import streamlit as st
from streamlit_tags import st_tags


def reverse_interest_map(d):
    reversed_ = defaultdict(set)

    for person, projects in d.items():
        for proj in projects:
            reversed_[proj].add(person)

    return reversed_


@st.experimental_memo
def possible_teams(leads, interested, max_people):
    teams = []

    for l in leads:
        for num_people in range(1, max_people + 1):
            teams.extend(
                [
                    {"lead": l, "people": list(people)}
                    for people in combinations(interested, num_people)
                    if l not in people
                ]
            )

    return teams


def is_valid(assignment, team_members, projects_per_person):
    people_to_num_projects = defaultdict(lambda: 0)

    for proj in assignment:
        people_to_num_projects[proj["lead"]] += 1
        for person in proj["people"]:
            people_to_num_projects[person] += 1

    for person in team_members:
        num_projects = people_to_num_projects[person]
        if num_projects < 1 or num_projects > projects_per_person:
            return False

    return True


@st.experimental_memo
def feasible_project_assignments(projs_to_teams, team_members, projects_per_person):
    assignments = []

    projects = list(projs_to_teams.keys())
    possible_teams = list(projs_to_teams.values())

    for possible_assignment in product(*possible_teams):
        if is_valid(possible_assignment, team_members, projects_per_person):
            a = {}

            for (proj, team) in zip(projects, possible_assignment):
                a[proj] = team

            assignments.append(a)

    return assignments


projects = st_tags(label="Projects")
team_members = st_tags(label="Team members")
people_per_project = st.sidebar.number_input(
    "Max (non-lead) people per project", min_value=1
)
projects_per_person = st.sidebar.number_input("Max projects per person", min_value=1)

lead_interest = {}
project_interest = {}

st.markdown("<br /> <br />", unsafe_allow_html=True)

for tm in team_members:
    with st.expander(f"{tm}'s choices"):
        want_to_lead = st.multiselect(
            "interested in leading", projects, key=f"{tm}_lead"
        )
        interested_in = st.multiselect(
            "interested in working on", projects, key=f"{tm}_interest"
        )

        lead_interest[tm] = set(want_to_lead)
        # We include projects that a team member wants to lead in the list of
        # projects they're interested in so that they can still be put on them
        # as a team member if feasible.
        project_interest[tm] = set([*want_to_lead, *interested_in])

st.markdown("<br /> <br />", unsafe_allow_html=True)

if st.button("Generate 10 random project assignments"):
    projects_to_leads = reverse_interest_map(lead_interest)
    projects_to_people = reverse_interest_map(project_interest)

    projs_to_teams = {}
    for proj in projects:
        possible_leads = projects_to_leads[proj]
        possible_people = projects_to_people[proj]
        projs_to_teams[proj] = possible_teams(
            possible_leads, possible_people, people_per_project
        )

    feasible_assignments = feasible_project_assignments(
        projs_to_teams, team_members, projects_per_person
    )

    sampled_assignments = sample(feasible_assignments, 10)
    for i, assignment in enumerate(sampled_assignments):
        st.write(f"Possible project assignment #{i}")
        st.write(assignment)
