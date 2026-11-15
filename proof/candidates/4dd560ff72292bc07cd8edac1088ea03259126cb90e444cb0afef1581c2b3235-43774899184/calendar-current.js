(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4dd560ff72292bc0.js","sha256":"4dd560ff72292bc07cd8edac1088ea03259126cb90e444cb0afef1581c2b3235","count":2109,"publishedAt":"2026-11-15T23:29:35Z","state":"calendar-state.json","stateSha256":"0d12f125b6fc0f69a3434e20f742626a9e55776dad356dd3db3d4e44265fba6f","sourceState":"calendar-source-state.json","sourceStateSha256":"8d517dcc3ca010f04ad4d372ac4e2b38ef3b1152cd5605062f6dc3491aac0906"});
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
