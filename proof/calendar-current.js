(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d56baf19b95b370e.js","sha256":"d56baf19b95b370e0d3504fe16e9fc7be2cea4aa8facc9910fac174a6a1d45d5","count":1741,"publishedAt":"2026-08-26T09:01:58Z","state":"calendar-state.json","stateSha256":"c62a69ff26df479dd2e1a365c39662b45afe9051b6ea3fd7fe40d584dccc2fd3"});
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
