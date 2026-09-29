(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2f86f1693080d202.js","sha256":"2f86f1693080d20284ef63ef3653f36f046755f9df2a83a191c7a8f2a2295381","count":2087,"publishedAt":"2026-09-29T01:03:50Z","state":"calendar-state.json","stateSha256":"d7680d9aad8494353cfe2fd0b0f4d67d92c2e2b1604bf8cc70cfaae9068861b4","sourceState":"calendar-source-state.json","sourceStateSha256":"fe042cd99a0bd644679f76af375e947c394b2eae59af21bc63dc152cf94ac84b"});
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
