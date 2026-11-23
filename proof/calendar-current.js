(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ce1c921f8b77b472.js","sha256":"ce1c921f8b77b4723592f3ec2d0c480ce7c968b123a535497d28d99b1c600440","count":2087,"publishedAt":"2026-11-23T01:47:38Z","state":"calendar-state.json","stateSha256":"a8cae7389a44ff9399421973be00f70f9c454327d6f11658b647123317cb67a7","sourceState":"calendar-source-state.json","sourceStateSha256":"29f9a8df287b44417a0970bac5070025e6dde73866a9e0c86c7b0c5031fcd7d3"});
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
