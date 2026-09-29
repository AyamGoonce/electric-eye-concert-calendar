(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cfa2b5fc0d9749f6.js","sha256":"cfa2b5fc0d9749f6e11a1875d80019f8831fea35eb73f686a9c59c9bc6411c99","count":2095,"publishedAt":"2026-09-29T09:55:45Z","state":"calendar-state.json","stateSha256":"004c9b055824f7488916eb6e7a6294bbd7d223ac86a25179bfc08a778772bf66","sourceState":"calendar-source-state.json","sourceStateSha256":"35a3749462690e81c34f8fe7674412e05c8bc62b743bf0b7844c34be001d962a"});
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
