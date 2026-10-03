(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1f0d580afb95a1b0.js","sha256":"1f0d580afb95a1b0af2fb43ce6dd3d6650294afd0bfa2f4ba4890ed794b9c40f","count":2203,"publishedAt":"2026-10-03T21:23:43Z","state":"calendar-state.json","stateSha256":"2bdcf931f9c0007dcd8a0282cd7cfc5ff80d8ac27fb69031b36a90324e2a1fe4","sourceState":"calendar-source-state.json","sourceStateSha256":"be521870b25262c17286326d20124e8fa55671e68d03d6437821618a066ca04a"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
