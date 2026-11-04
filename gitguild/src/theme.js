/* Theme boot + controls. This file is inlined in every static page. */
(function () {
  'use strict';

  var root = document.documentElement;
  var themeKey = 'gitguild-theme';
  var soundKey = 'gitguild-theme-sound';
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null;
  var savedTheme = null;
  var soundEnabled = false;
  var audioContext = null;

  try {
    savedTheme = localStorage.getItem(themeKey);
    soundEnabled = localStorage.getItem(soundKey) === 'on';
  } catch (error) {}

  var followsSystem = savedTheme !== 'light' && savedTheme !== 'dark';
  function systemTheme() { return media && media.matches ? 'light' : 'dark'; }
  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'light' ? '#F4F0E6' : '#0A0D11');
    var button = document.querySelector('[data-theme-toggle]');
    if (button) {
      var label = theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme';
      button.setAttribute('aria-label', label);
      button.setAttribute('title', label);
    }
  }
  setTheme(followsSystem ? systemTheme() : savedTheme);

  function playClick() {
    var Audio = window.AudioContext || window.webkitAudioContext;
    if (!Audio) return;
    try {
      audioContext = audioContext || new Audio();
      if (audioContext.state === 'suspended') audioContext.resume();
      var length = Math.max(1, Math.floor(audioContext.sampleRate * .024));
      var buffer = audioContext.createBuffer(1, length, audioContext.sampleRate);
      var channel = buffer.getChannelData(0);
      for (var i = 0; i < length; i += 1) {
        var fade = 1 - i / length;
        channel[i] = (Math.random() * 2 - 1) * fade * fade;
      }
      var source = audioContext.createBufferSource();
      var filter = audioContext.createBiquadFilter();
      var gain = audioContext.createGain();
      source.buffer = buffer;
      filter.type = 'bandpass';
      filter.frequency.value = 1500;
      filter.Q.value = .8;
      gain.gain.setValueAtTime(.0001, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(.045, audioContext.currentTime + .002);
      gain.gain.exponentialRampToValueAtTime(.0001, audioContext.currentTime + .028);
      source.connect(filter);
      filter.connect(gain);
      gain.connect(audioContext.destination);
      source.start();
      source.stop(audioContext.currentTime + .03);
    } catch (error) {}
  }

  function applyTheme(theme, persist) {
    setTheme(theme);
    if (persist) {
      followsSystem = false;
      try { localStorage.setItem(themeKey, theme); } catch (error) {}
    }
    var status = document.querySelector('[data-theme-status]');
    if (status) status.textContent = (theme === 'light' ? 'Light' : 'Dark') + ' theme enabled';
  }

  function initializeControls() {
    var themeButton = document.querySelector('[data-theme-toggle]');
    var soundButton = document.querySelector('[data-sound-toggle]');
    if (!themeButton || !soundButton) return;

    function updateSoundButton() {
      soundButton.setAttribute('aria-pressed', soundEnabled ? 'true' : 'false');
      var label = soundEnabled ? 'Mute theme click sound' : 'Enable theme click sound';
      soundButton.setAttribute('aria-label', label);
      soundButton.setAttribute('title', label);
    }
    updateSoundButton();

    themeButton.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      var rect = themeButton.getBoundingClientRect();
      root.style.setProperty('--theme-x', (rect.left + rect.width / 2) + 'px');
      root.style.setProperty('--theme-y', (rect.top + rect.height / 2) + 'px');
      if (soundEnabled) playClick();
      var reduced = media && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var change = function () { applyTheme(next, true); };
      if (!reduced && document.startViewTransition) {
        document.startViewTransition(change);
      } else if (!reduced) {
        root.classList.add('theme-fallback');
        change();
        window.setTimeout(function () { root.classList.remove('theme-fallback'); }, 500);
      } else {
        change();
      }
    });

    soundButton.addEventListener('click', function () {
      soundEnabled = !soundEnabled;
      try { localStorage.setItem(soundKey, soundEnabled ? 'on' : 'off'); } catch (error) {}
      updateSoundButton();
      if (soundEnabled) playClick();
    });

    if (media && media.addEventListener) {
      media.addEventListener('change', function (event) {
        if (followsSystem) applyTheme(event.matches ? 'light' : 'dark', false);
      });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initializeControls);
  else initializeControls();
})();
