'use strict';

// Upload file bytes directly to private storage. Only signed file receipts and
// the form's text fields pass through Django/Vercel Functions.
if (document.body.dataset.blobUploadUrl) {
  document.querySelectorAll('form').forEach(form => {
    const uploaded = new WeakMap();
    form.addEventListener('submit', async event => {
      const inputs = [...form.querySelectorAll('input[type="file"]:not(:disabled)')]
        .filter(input => input.files.length);
      if (!inputs.length) return;
      event.preventDefault();
      if (form.dataset.blobBusy === 'true') return;
      const files = inputs.map(input => ({input, file: input.files[0]}));
      let status = form.querySelector('[data-blob-status]');
      if (!status) {
        status = document.createElement('p');
        status.dataset.blobStatus = 'true';
        status.setAttribute('role', 'status');
        form.append(status);
      }
      if (files.some(({file}) => file.size > 30 * 1024 * 1024 || file.size === 0)) {
        status.textContent = 'Choose non-empty files up to 30 MB each.';
        return;
      }
      if (files.reduce((size, {file}) => size + file.size, 0) > 32 * 1024 * 1024) {
        status.textContent = 'Total attachments must be at most 32 MB per form.';
        return;
      }
      form.dataset.blobBusy = 'true';
      form.setAttribute('aria-busy', 'true');
      const button = event.submitter;
      const label = button?.textContent;
      if (button) { button.disabled = true; button.textContent = 'Uploading...'; }
      try {
        for (const [index, {input, file}] of files.entries()) {
          status.textContent = `Uploading file ${index + 1} of ${files.length}...`;
          let receipt = uploaded.get(file);
          if (!receipt || receipt.field !== input.name || Date.now() - receipt.created > 25 * 60 * 1000) {
            const response = await fetch(document.body.dataset.blobUploadUrl, {
              method: 'POST', credentials: 'same-origin',
              headers: {'Content-Type': 'application/json',
                'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value},
              body: JSON.stringify({path: new URL(form.action || location.href).pathname,
                field: input.name, filename: file.name, size: file.size}),
            });
            if (!response.ok || response.redirected) {
              const details = await response.json().catch(() => ({}));
              throw new Error(details.error || 'Unable to start the upload. Refresh the page and try again.');
            }
            const details = await response.json();
            const upload = await fetch(details.url, {method: 'PUT', body: file,
              credentials: 'omit', headers: {'Content-Type': details.content_type}});
            if (!upload.ok) throw new Error('The upload failed. Please try again.');
            receipt = {ticket: details.ticket, created: Date.now(), field: input.name};
            uploaded.set(file, receipt);
          }
          const hidden = document.createElement('input');
          hidden.type = 'hidden'; hidden.name = '_blob_' + input.name;
          hidden.value = receipt.ticket; hidden.dataset.blobTicket = 'true';
          form.append(hidden);
        }
        status.textContent = 'Checking files and saving...';
        inputs.forEach(input => { input.disabled = true; });
        // Native submission preserves CSRF and all normal form fields while
        // omitting the binary inputs; bypass the duplicate-submit listeners.
        HTMLFormElement.prototype.submit.call(form);
      } catch (error) {
        status.textContent = error instanceof TypeError
          ? 'Upload connection failed. Please check your connection and try again.'
          : error.message;
        form.querySelectorAll('[data-blob-ticket]').forEach(input => input.remove());
        inputs.forEach(input => { input.disabled = false; });
        delete form.dataset.blobBusy;
        form.removeAttribute('aria-busy');
        if (button) { button.disabled = false; button.textContent = label; }
      }
    });
  });
}

if (document.body.dataset.uploadsEnabled === 'false') {
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.disabled = true;
    const note = document.createElement('p');
    note.className = 'muted';
    note.textContent = 'File uploads are temporarily unavailable. Optional attachments can be left out.';
    input.insertAdjacentElement('afterend', note);
    if (input.required) {
      note.textContent = 'File uploads are temporarily unavailable. Please contact your director for this resource.';
      input.closest('form')?.querySelectorAll('button[type="submit"], button:not([type])').forEach(button => {
        button.disabled = true;
      });
    }
  });
}

// Show feedback during normal form navigation and prevent duplicate submissions.
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', event => {
    if (event.defaultPrevented || form.target === '_blank') return;
    if (form.dataset.submitting === 'true') {
      event.preventDefault();
      return;
    }
    form.dataset.submitting = 'true';
    form.setAttribute('aria-busy', 'true');
    const button = event.submitter;
    if (button && button.tagName === 'BUTTON') {
      button.dataset.originalLabel = button.textContent;
      button.textContent = form.method.toLowerCase() === 'get' ? 'Searching...' : 'Please wait...';
      button.setAttribute('aria-disabled', 'true');
    }
  });
});
window.addEventListener('pageshow', () => {
  document.querySelectorAll('form[data-submitting]').forEach(form => {
    delete form.dataset.submitting;
    form.removeAttribute('aria-busy');
    form.querySelectorAll('[data-original-label]').forEach(button => {
      button.textContent = button.dataset.originalLabel;
      delete button.dataset.originalLabel;
      button.removeAttribute('aria-disabled');
    });
  });
});
document.querySelectorAll('.sidebar nav a').forEach(link => {
  if (new URL(link.href).pathname === location.pathname) {
    link.classList.add('active');
    link.setAttribute('aria-current', 'page');
  }
});
const menu = document.querySelector('.menu-toggle');
menu?.addEventListener('click', () => {
  const open = document.querySelector('.sidebar').classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
});
document.addEventListener('keydown', e => {
  if(e.key === 'Escape') {
    document.querySelector('.sidebar')?.classList.remove('open');
    menu?.setAttribute('aria-expanded', 'false');
  }
});
document.querySelector('#add-question')?.addEventListener('click', () => {
  const total = document.querySelector('#id_questions-TOTAL_FORMS');
  const count = Number(total.value);
  if (count >= 50) return;
  const markup = document.querySelector('#empty-question').innerHTML.replaceAll('__prefix__', String(count));
  document.querySelector('#question-forms').insertAdjacentHTML('beforeend', markup);
  setupQuestionOptions(document.querySelector('#question-forms').lastElementChild);
  total.value = String(count + 1);
  if (count + 1 >= 50) document.querySelector('#add-question').disabled = true;
});

document.querySelectorAll('[data-carousel]').forEach(carousel => {
  const slides = [...carousel.querySelectorAll('[data-slide]')];
  const dots = [...carousel.querySelectorAll('[data-slide-to]')];
  const status = carousel.querySelector('[data-carousel-status]');
  const stage = carousel.querySelector('.carousel-stage');
  if (slides.length < 2) return;
  let current = 0;
  let touchStart = null;

  const showSlide = index => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, position) => { slide.hidden = position !== current; });
    dots.forEach((dot, position) => {
      if (position === current) dot.setAttribute('aria-current', 'true');
      else dot.removeAttribute('aria-current');
    });
    status.textContent = `Photo ${current + 1} of ${slides.length}`;
  };

  carousel.querySelector('[data-carousel-prev]').addEventListener('click', () => showSlide(current - 1));
  carousel.querySelector('[data-carousel-next]').addEventListener('click', () => showSlide(current + 1));
  dots.forEach(dot => dot.addEventListener('click', () => showSlide(Number(dot.dataset.slideTo))));
  carousel.addEventListener('keydown', event => {
    const destinations = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1 };
    if (Object.hasOwn(destinations, event.key)) {
      event.preventDefault();
      showSlide(destinations[event.key]);
    }
  });
  stage.addEventListener('pointerdown', event => {
    if (event.pointerType === 'touch' && !event.target.closest('button')) {
      touchStart = { x: event.clientX, y: event.clientY };
    }
  });
  stage.addEventListener('pointerup', event => {
    if (!touchStart) return;
    const deltaX = event.clientX - touchStart.x;
    const deltaY = event.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY)) {
      showSlide(current + (deltaX < 0 ? 1 : -1));
    }
  });
  stage.addEventListener('pointercancel', () => { touchStart = null; });
});


function setupQuestionOptions(question) {
  const countInput = question.querySelector('input[name$="-option_count"]');
  if (!countInput) return;
  let count = Math.max(2, Math.min(26, Number(countInput.value) || 4));
  const controls = document.createElement('div');
  controls.className = 'form-actions';
  const status = document.createElement('span');
  status.setAttribute('aria-live', 'polite');
  const add = document.createElement('button');
  add.type = 'button'; add.className = 'secondary'; add.textContent = '+ Add option';
  const remove = document.createElement('button');
  remove.type = 'button'; remove.className = 'secondary'; remove.textContent = 'Remove last option';
  controls.append(add, remove, status);
  question.querySelector('input[name$="-option_a"]').closest('p').before(controls);
  const refresh = () => {
    countInput.value = String(count);
    status.textContent = `${count} options (minimum 2, maximum 26)`;
    add.disabled = count >= 26; remove.disabled = count <= 2;
    for (let i = 0; i < 26; i++) {
      const input = question.querySelector(`input[name$="-option_${String.fromCharCode(97+i)}"]`);
      input.closest('p').hidden = i >= count;
      input.disabled = i >= count;
      input.required = i < count;
      const answer = question.querySelector(`input[name$="-correct"][value="${String.fromCharCode(65+i)}"]`);
      answer.closest('label').parentElement.hidden = i >= count;
      answer.disabled = i >= count;
      if (i >= count) answer.checked = false;
    }
  };
  add.addEventListener('click', () => { if (count < 26) { count++; refresh(); } });
  remove.addEventListener('click', () => { if (count > 2) { count--; refresh(); } });
  const multiple = question.querySelector('input[name$="-is_multiple"]');
  const help = document.createElement('p');
  help.className = 'muted';
  help.textContent = 'Tick all correct answers below. Selecting more than one enables multiple answers automatically.';
  question.querySelector('input[name$="-correct"]').closest('div[id]').before(help);
  question.addEventListener('change', event => {
    const answers = [...question.querySelectorAll('input[name$="-correct"]:checked')];
    if (event.target.name.endsWith('-correct') && answers.length > 1) multiple.checked = true;
    if (event.target === multiple && !multiple.checked) answers.slice(1).forEach(answer => { answer.checked = false; });
  });
  refresh();
}
document.querySelectorAll('#question-forms .question-form').forEach(setupQuestionOptions);


// Features shares the home URL; show its dashboard shortcut only in that view.
const featuresWorkspace = document.querySelector('[data-features-workspace]');
if (featuresWorkspace) {
  const updateWorkspaceVisibility = () => {
    featuresWorkspace.hidden = window.location.hash !== '#features';
  };
  window.addEventListener('hashchange', updateWorkspaceVisibility);
  updateWorkspaceVisibility();
}


const resourceCategory = document.querySelector('select[name="category"]');
const customCategory = document.querySelector('input[name="custom_category"]');
if (resourceCategory && customCategory) {
  const updateCustomCategory = () => {
    const isCustom = resourceCategory.value === '__custom__';
    customCategory.closest('p').hidden = !isCustom;
    customCategory.disabled = !isCustom;
    customCategory.required = isCustom;
  };
  resourceCategory.addEventListener('change', updateCustomCategory);
  updateCustomCategory();
}
