(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.633104a883aa3ccf.js","sha256":"633104a883aa3ccfa9126ae92675ca8a6588f0f16ccaa120ba3e183f3c2a0edf","count":2049,"publishedAt":"2026-10-26T13:14:55Z","state":"calendar-state.json","stateSha256":"52debceb124ebd2d251e37bc295d2f926245b761d36d8babd8e4d6ca9fc23b00","sourceState":"calendar-source-state.json","sourceStateSha256":"ab150fc59445c7504d9a65c716f83f362a5f4592c33181cf5f1cbbbc37537b4f"});
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
