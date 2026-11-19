(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c3a6c79ff5c95478.js","sha256":"c3a6c79ff5c95478b11a999fdcbfa5dd08caa0b7328d2bfde8198ee53699c0de","count":2131,"publishedAt":"2026-11-19T11:49:28Z","state":"calendar-state.json","stateSha256":"9a249cb2546b532222cd24cd44871e581b6595e3a2d8c2d9283fc9a5a1a11631","sourceState":"calendar-source-state.json","sourceStateSha256":"1bfedc94063d53cadc30c36af273df1be8d93813728bfd5f9ae5f3c3e1eb7670"});
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
