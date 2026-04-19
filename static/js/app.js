const formationGrid = document.getElementById('formationGrid');
const categoryFilter = document.getElementById('categoryFilter');
const userMenuButton = document.getElementById('userMenuButton');
const userDropdown = document.getElementById('userDropdown');
const isAdmin = window.App?.isAdmin;
let formations = [];

const formatCard = (formation) => {
  const card = document.createElement('article');
  card.className = 'card';

  const metaRow = document.createElement('div');
  metaRow.className = 'card-meta';

  const categoryPill = document.createElement('span');
  categoryPill.className = 'category-pill';
  categoryPill.textContent = formation.category;

  const duration = document.createElement('span');
  duration.className = 'duration';
  duration.textContent = formation.duration;

  const seats = document.createElement('span');
  seats.className = 'seats-info';
  seats.textContent = `${formation.available_seats} seats available`;

  metaRow.append(categoryPill, duration, seats);

  const title = document.createElement('h2');
  title.className = 'card-title';

  const titleLink = document.createElement('a');
  titleLink.className = 'card-link';
  titleLink.href = `/formations/${formation.id}`;
  titleLink.textContent = formation.title;

  title.appendChild(titleLink);

  const description = document.createElement('p');
  description.className = 'card-description';
  description.textContent = formation.description;

  card.append(metaRow, title, description);

  if (isAdmin) {
    const actions = document.createElement('div');
    actions.className = 'card-actions';

    const editLink = document.createElement('a');
    editLink.href = `/admin/formations/${formation.id}/edit`;
    editLink.className = 'action-button edit-button';
    editLink.title = 'Edit formation';
    editLink.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 17.25V21h3.75L17.81 10.94l-3.75-3.75L4 17.25Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M14.06 5.94 18.06 9.94" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'action-button delete-button';
    deleteButton.title = 'Delete formation';
    deleteButton.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 6h18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M8 6V4h8v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M19 6 18.17 19a2 2 0 0 1-2 1.95H7.83A2 2 0 0 1 5.83 19L5 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M10 11v6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M14 11v6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      </svg>
    `;
    deleteButton.addEventListener('click', async () => {
      if (!confirm(`Delete formation “${formation.title}”? This cannot be undone.`)) {
        return;
      }
      try {
        const response = await fetch(`/admin/formations/${formation.id}/delete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) {
          throw new Error('Unable to delete formation');
        }
        loadFormations();
      } catch (error) {
        console.error(error);
        alert('Unable to delete formation.');
      }
    });

    actions.append(editLink, deleteButton);
    card.append(actions);
  }

  return card;
};

const renderFormations = (items) => {
  formationGrid.innerHTML = '';

  if (!items.length) {
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-state';
    emptyState.textContent = 'No formations match this category yet.';
    formationGrid.appendChild(emptyState);
    return;
  }

  const fragment = document.createDocumentFragment();
  items.forEach((formation) => fragment.appendChild(formatCard(formation)));
  formationGrid.appendChild(fragment);
};

const updateFilterOptions = (items) => {
  const categories = Array.from(new Set(items.map((item) => item.category))).sort();
  categories.forEach((category) => {
    const option = document.createElement('option');
    option.value = category;
    option.textContent = category;
    categoryFilter.appendChild(option);
  });
};

const filterSelections = () => {
  const selectedCategory = categoryFilter.value;
  const filtered = selectedCategory === 'all'
    ? formations
    : formations.filter((item) => item.category === selectedCategory);

  renderFormations(filtered);
};

const loadFormations = async () => {
  try {
    const response = await fetch('/api/formations');
    if (!response.ok) {
      throw new Error('Failed to fetch formations');
    }

    const data = await response.json();
    formations = data.formations || [];
    updateFilterOptions(formations);
    renderFormations(formations);
  } catch (error) {
    formationGrid.innerHTML = '<div class="empty-state">Unable to load formation data. Please try again later.</div>';
    console.error(error);
  }
};

const closeDropdown = (event) => {
  if (!event.target.closest('.user-menu')) {
    userDropdown?.classList.remove('active');
  }
};

userMenuButton?.addEventListener('click', (event) => {
  event.stopPropagation();
  userDropdown?.classList.toggle('active');
});

document.addEventListener('click', closeDropdown);
window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    userDropdown?.classList.remove('active');
  }
});

categoryFilter.addEventListener('change', filterSelections);
loadFormations();
