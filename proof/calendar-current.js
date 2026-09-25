(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ee71c9b68ff99f8e.js","sha256":"ee71c9b68ff99f8e10a8bb2b7e8f616b44a20537fd595c0ea981ee44db84ad0e","count":2123,"publishedAt":"2026-09-25T17:17:05Z","state":"calendar-state.json","stateSha256":"888f760077714a998017b9b615b2ff3c3f6849afdacb005e31569d97bebbf451","sourceState":"calendar-source-state.json","sourceStateSha256":"123a5cfc9acafef3e6cb646ad3f928ff5c6683e3f1d88a0d733b8927bbaab0d9"});
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
