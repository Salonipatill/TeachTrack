'use strict';

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
