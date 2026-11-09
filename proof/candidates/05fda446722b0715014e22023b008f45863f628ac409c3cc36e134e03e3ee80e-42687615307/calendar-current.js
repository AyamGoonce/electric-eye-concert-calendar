(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.05fda446722b0715.js","sha256":"05fda446722b0715014e22023b008f45863f628ac409c3cc36e134e03e3ee80e","count":2206,"publishedAt":"2026-11-09T19:53:33Z","state":"calendar-state.json","stateSha256":"11510f1ad27e31bf03e7c2f5d5faeed1df0a59d7631b5d4e0957093bafb6e8ad","sourceState":"calendar-source-state.json","sourceStateSha256":"a654ae2b35d1ec24f7cae5340757b96cebcc137ae9789569f43191d6f9467c71"});
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
