(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.36ef9295a2063df2.js","sha256":"36ef9295a2063df20601fc76c52e494dfe7e38f0d91f13506df3442add34ade9","count":2126,"publishedAt":"2026-11-27T15:26:47Z","state":"calendar-state.json","stateSha256":"df09feadc970c9cc764f94d1f9166369d938b4ea73a90a13793870c1381fd544","sourceState":"calendar-source-state.json","sourceStateSha256":"a4f8065c8e53300c5430e5f053abd32fd9f51bfd41aa0caba6d5187f5fb8a782"});
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
